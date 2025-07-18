import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import json
from scipy.spatial import Delaunay
from PIL import Image
import matplotlib.colors as mcolors
from matplotlib.colorbar import ColorbarBase
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap

def define_contour(dermatomes):
    without_contours = dermatomes.copy()
    uniques = sorted(np.unique(without_contours))[1:]
    for unique in uniques:
        binary_img = (without_contours == unique).astype('uint8')
        contours, _ = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        dermatomes = cv2.drawContours(dermatomes, contours, -1, 255, 1)
    return dermatomes

def no_rigid_registration(fixed_image, moving_image):
    # binarizar
    bF = (fixed_image>0).astype(np.uint8)*255
    bM = (moving_image>0).astype(np.uint8)*255
    cF,_ = cv2.findContours(bF, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cM,_ = cv2.findContours(bM, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cntF = max(cF, key=cv2.contourArea).reshape(-1,2)
    cntM = max(cM, key=cv2.contourArea).reshape(-1,2)
    N = 200
    idxF = np.linspace(0,len(cntF)-1,N).astype(int)
    idxM = np.linspace(0,len(cntM)-1,N).astype(int)
    pts_dst = cntF[idxF].astype(np.float32)
    pts_src = cntM[idxM].astype(np.float32)
    tri = Delaunay(pts_dst)
    return pts_src, pts_dst, tri.simplices

def resample(moving_image, fixed_image, reg):
    pts_src, pts_dst, tris = reg
    h,w = fixed_image.shape[:2]
    out = np.zeros_like(moving_image)
    for tri_inds in tris:
        src = pts_src[tri_inds].astype(np.float32)
        dst = pts_dst[tri_inds].astype(np.float32)
        mask = np.zeros((h,w),np.uint8)
        cv2.fillConvexPoly(mask, np.int32(dst),1)
        M = cv2.getAffineTransform(src,dst)
        warped = cv2.warpAffine(moving_image, M, (w,h),
                               flags=cv2.INTER_NEAREST,
                               borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        out[mask==1]=warped[mask==1]
    return out

def register_one_foot(foot_mask, derm_template):
    h,w = foot_mask.shape[:2]
    tmpl_resized = cv2.resize(derm_template,(w,h),interpolation=cv2.INTER_NEAREST)
    reg = no_rigid_registration(fixed_image=foot_mask, moving_image=tmpl_resized)
    return resample(moving_image=tmpl_resized,
                    fixed_image=foot_mask,
                    reg=reg)

def extract_feet(mask):
    """Extrae uno o dos pies (ROIs) y sus coordenadas a partir de una máscara binaria."""
    # Asegurarse de que mask sea 2D
    if mask.ndim != 2:
        mask = mask[:, :, 0]
    img = mask.astype('uint8')
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return None, None, []

    contours = list(contours)
    # Ordenamos de mayor a menor según el área
    contours.sort(reverse=True, key=lambda c: cv2.contourArea(c))

    coord = []
    # Procesamos hasta dos contornos
    for c in contours[:2]:
        yBot = c[c[:, :, 1].argmax()][0][1]
        xRig = c[c[:, :, 0].argmin()][0][0]
        yTop = c[c[:, :, 1].argmin()][0][1]
        xLef = c[c[:, :, 0].argmax()][0][0]
        coord.append([yTop, yBot, xRig, xLef, c])

    # Si solo se detectó un contorno, usar ese para el pie derecho y dejar el izquierdo en None
    if len(coord) == 1:
        right_foot = np.zeros_like(img)
        right_foot = cv2.drawContours(right_foot, [coord[0][-1]], -1, 1, -1)
        right_foot = right_foot[coord[0][0]:coord[0][1], coord[0][2]:coord[0][3]]
        return right_foot, None, coord

    # Si se detectaron dos, ordenar por la coordenada x para asignar derecha e izquierda
    coord.sort(key=lambda x: x[2])
    right_foot = np.zeros_like(img)
    right_foot = cv2.drawContours(right_foot, [coord[0][-1]], -1, 1, -1)
    right_foot = right_foot[coord[0][0]:coord[0][1], coord[0][2]:coord[0][3]]

    left_foot = np.zeros_like(img)
    left_foot = cv2.drawContours(left_foot, [coord[1][-1]], -1, 1, -1)
    left_foot = left_foot[coord[1][0]:coord[1][1], coord[1][2]:coord[1][3]]

    return right_foot, left_foot, coord

def get_dermatomes(fixed_mask, path_right_foot, path_left_foot):
    """
    Genera la imagen de dermatomas registrados:
      - fixed_mask: máscara binaria obtenida de YOLO (255 donde hay pie).
      - path_right_foot y path_left_foot: rutas a las plantillas en escala de grises.
    """
    fixed_mask = np.squeeze(fixed_mask)

    right_img = cv2.imread(path_right_foot, cv2.IMREAD_GRAYSCALE)
    if right_img is None:
        raise FileNotFoundError(f"Plantilla derecha no encontrada: {path_right_foot}")
    right_dermatomes = cv2.flip(right_img, 1)

    left_dermatomes = cv2.imread(path_left_foot, cv2.IMREAD_GRAYSCALE)
    if left_dermatomes is None:
        raise FileNotFoundError(f"Plantilla izquierda no encontrada: {path_left_foot}")

    left_dermatomes[left_dermatomes != 0] = left_dermatomes[left_dermatomes != 0] + 1

    right_foot, left_foot, coord = extract_feet(fixed_mask)

    # Registrar dermatomas para el pie derecho
    if right_foot is not None:
        right_dermatomes_registered = register_one_foot(right_foot, right_dermatomes)
        output_dermatomes = np.zeros_like(fixed_mask, dtype='float')
        output_dermatomes[coord[0][0]:coord[0][1], coord[0][2]:coord[0][3]] = right_dermatomes_registered
    else:
        output_dermatomes = np.zeros_like(fixed_mask, dtype='float')

    # Si se detectó también el pie izquierdo, registrarlo y sumarlo
    if left_foot is not None and len(coord) >= 2:
        left_dermatomes_registered = register_one_foot(left_foot, left_dermatomes)
        output_dermatomes[coord[1][0]:coord[1][1], coord[1][2]:coord[1][3]] += left_dermatomes_registered

    output_dermatomes = define_contour(output_dermatomes)
    return output_dermatomes

def overlay_dermatomes_on_image(orig, derms):
    gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    out = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    for lbl in np.unique(derms):
        if lbl in (0,255): continue
        mask = (derms==lbl).astype(np.uint8)
        cnts,_ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(out, cnts, -1, (0,0,255),2)
    return out

def compute_dermatome_temperatures(temp_map, derms):
    dic = {
        10:'Medial PD',11:'Medial PI',
        20:'Lateral PD',21:'Lateral PI',
        30:'Sural PD',31:'Sural PI',
        40:'Tibial PD',41:'Tibial PI',
        50:'Saphenous PD',51:'Saphenous PI'
    }
    res = {}
    labels = [l for l in np.unique(derms) if l not in (0,255)]
    for k,name in dic.items():
        if k in labels:
            mask = derms==k
            res[name]= float(temp_map[mask].mean())
    return res

def make_both_feet_colored(
    template_path: str,
    temps_right: dict,
    temps_left: dict,
    mn: float,
    mx: float,
    out_path: str
):
    """
    - template_path: plantilla en gris con etiquetas 10,20,30… para el pie derecho.
    - temps_right: dict de zonas PD (ej 'Medial PD':29.3).
    - temps_left:  dict de zonas PI  (ej 'Medial PI':28.7).
    - mn,mx: rango min/max para el colormap.
    - out_path: ruta donde salvar el PNG.
    """

    # 1) Colormap + muchos bins para mayor resolución

    colors = [
        '#0000FF',  # azul puro
        '#FF0000'   # rojo puro
    ]
    cmap = LinearSegmentedColormap.from_list('BlueToRed', colors, N=256)
    bins = np.linspace(mn, mx, 50)  # niveles de color entre mn y mx
    norm = mcolors.BoundaryNorm(bins, ncolors=cmap.N, clip=True)
    sm   = cm.ScalarMappable(norm=norm, cmap=cmap)

    # 2) Mapa nombre→etiqueta
    name2label = {
        'Medial PD':10, 'Lateral PD':20, 'Sural PD':30,
        'Tibial PD':40,'Saphenous PD':50,
        'Medial PI':11, 'Lateral PI':21,'Sural PI':31,
        'Tibial PI':41,'Saphenous PI':51
    }

    # 3) Cargo la plantilla original (derecho)
    tmpl = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if tmpl is None:
        raise FileNotFoundError(f"No pude leer plantilla: {template_path}")
    h, w = tmpl.shape

    # 4) Genero la plantilla para el izquierdo desplazando etiquetas +1
    left_tmpl = tmpl.copy()
    left_tmpl[left_tmpl != 0] += 1

    # 5) Preparo buffers RGBA
    right_col = np.zeros((h, w, 4), dtype=np.uint8)
    left_col  = np.zeros((h, w, 4), dtype=np.uint8)

    # 6) Pinto el pie derecho sobre right_col
    for name, temp in temps_right.items():
        lbl  = name2label[name]
        mask = (tmpl == lbl)
        rgba = (np.array(sm.to_rgba(temp)) * 255).astype(np.uint8)
        right_col[mask] = rgba

    contours_map = define_contour(tmpl.astype('float'))
    uniques = sorted(np.unique(contours_map))[1:]

    for u in uniques:
        bin_mask = (contours_map == u).astype('uint8')
        cnts, _  = cv2.findContours(bin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(right_col, cnts, -1, (0,0,0,255), 1)

    # 7) Pinto el pie izquierdo sobre left_col usando left_tmpl
    for name, temp in temps_left.items():
        lbl  = name2label[name]
        mask = (left_tmpl == lbl)
        rgba = (np.array(sm.to_rgba(temp)) * 255).astype(np.uint8)
        left_col[mask] = rgba

    contours_map_left = define_contour(left_tmpl.astype('float'))
    uniques_left = sorted(np.unique(contours_map_left))[1:]

    for u in uniques_left:
        bin_mask = (contours_map_left == u).astype('uint8')
        cnts, _  = cv2.findContours(bin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(left_col, cnts, -1, (0,0,0,255), 1)

    # Anotar nombres, con rotación para algunas zonas
    def annotate(ax, label_map, mapping, is_left: bool):
        for name, lbl in mapping.items():
            # coordenadas en la plantilla correcta (antes de invertir)
            ref_map = tmpl if is_left else left_tmpl
            bin_mask = (ref_map == lbl).astype('uint8')
            cnts,_ = cv2.findContours(bin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not cnts: continue
            pts = np.vstack(cnts).squeeze()
            M = cv2.moments(pts)
            if M['m00']==0: continue
            cx = M['m10']/M['m00']
            cy = M['m01']/M['m00']
            # área para escalar fuente
            area = M['m00']
            font_size = max(12, min(36, int(np.sqrt(area)/4)))

            # Si es una de las zonas largas, la rotamos
            angle = 0
            if any(s in name for s in ("Lateral", "Sural", "Saphenous")):
                angle = 90

            ax.text(
                cx if not is_left else w - cx,  # corregir x para pie invertido
                cy,
                name,
                color='black',
                fontsize=font_size,
                ha='center',
                va='center',
                rotation=angle,
                weight='bold'
            )

    # 8) Ahora sí, invierto horizontalmente SOLO el izquierdo
    right_col = np.fliplr(right_col)

    # 9) Dibujo los dos pies y la barra de color
    fig, (ax_r, ax_l, ax_cb) = plt.subplots(
        1, 3, figsize=(12, 12),
        gridspec_kw={'width_ratios':[1,1,0.2]}
    )

    ax_r.imshow(right_col); ax_r.axis('off')
    ax_l.imshow(left_col ); ax_l.axis('off')

    # Anotar nombres
    annotate(
        ax_r,
        tmpl,
        { name: name2label[name] for name in temps_right.keys() },
        is_left=True
    )
    annotate(
        ax_l,
        left_tmpl,
        { name: name2label[name] for name in temps_left.keys() },
        is_left=False
    )

    cb = ColorbarBase(ax_cb, cmap=cmap, norm=norm, orientation='vertical')
    cb.set_label('Temperatura (°C)')
    cb.set_ticks([mn, mx])
    cb.set_ticklabels([f"{mn:.1f}", f"{mx:.1f}"])

    # ——— 1) Subir tamaño de texto de la colorbar ———
    cb.ax.tick_params(labelsize=20)             # etiquetas de ticks
    cb.ax.yaxis.label.set_size(22)              # etiqueta 'Temperatura (°C)'

    # ——— 2) Dibujar un marco negro alrededor de los pies ———
    for ax in (ax_r, ax_l):
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor('black')
            spine.set_linewidth(2)

    # (Opcional) contornear la colorbar también:
    for spine in ax_cb.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor('black')
        spine.set_linewidth(2)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def run_plot(image_path, files_dir, max_temp_str, min_temp_str):
   # 0) Comprueba que mask.png existe
    mask_path = os.path.join(files_dir, "mask.png")
    if not os.path.isfile(mask_path):
        raise FileNotFoundError(f"¡No existe mask.png en: {mask_path}")
    # 1) Segmentación
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"cv2.imread image_path devolvió None para: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError(f"cv2.imread mask.png devolvió None para: {mask_path}")

    # redimensionar la máscara 512×512 → al tamaño de la imagen original
    H, W = img.shape[:2]
    mask = cv2.resize(mask, (W, H), interpolation=cv2.INTER_NEAREST)
    # Guarda figura original+mask
    seg_png = os.path.join(files_dir, "segmentation_plot.png")
    fig,axs = plt.subplots(1,2,figsize=(12,6))
    axs[0].imshow(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)); axs[0].axis("off")
    axs[1].imshow(mask, cmap="gray");            axs[1].axis("off")
    plt.savefig(seg_png, bbox_inches="tight"); plt.close(fig)

    # 2) Overlay de segmentación
    overlay_seg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    cnts,_     = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay_seg, cnts, -1, (0,0,255),2)
    seg_overlay_png = os.path.join(files_dir, "seg_overlay.png")
    cv2.imwrite(seg_overlay_png, overlay_seg)

    # 3) Registro dermatomas
    base = os.path.dirname(__file__)
    right_t = os.path.join(base, "templates", "dermatomes.png")
    left_t  = os.path.join(base, "templates", "dermatomes.png")
    derms  = get_dermatomes(mask, right_t, left_t)
    overlay_derm = overlay_dermatomes_on_image(img, derms)
    derm_overlay_png = os.path.join(files_dir, "derm_contours.png")
    cv2.imwrite(derm_overlay_png, overlay_derm)

    # 4) Temperaturas
    mx = float(max_temp_str); mn = float(min_temp_str)
    temp_map = (img.astype(np.float32)/255)*(mx-mn)+mn
    temps_dict = compute_dermatome_temperatures(temp_map, derms)

    # Separa según sufijo:
    temps_right = {k: v for k, v in temps_dict.items() if k.endswith("PD")}
    temps_left  = {k: v for k, v in temps_dict.items() if k.endswith("PI")}

    colored_path = os.path.join(files_dir, "derm_colored_both.png")
    make_both_feet_colored(
        right_t,
        temps_right,
        temps_left,
        24.0, 34.0,
        colored_path
    )

    return derm_overlay_png, json.dumps(temps_dict), colored_path