
import numpy as np
from scipy.interpolate import interp1d
from matplotlib.patches import Wedge
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


def internal_clades_angles(clade, angles):
    for subclade in clade:
        if subclade not in angles:
            internal_clades_angles(subclade, angles)

    # Closure over heights
    angles[clade] = (angles[clade.clades[0]] + angles[clade.clades[-1]]) / 2.0


def clade_angles(tree, arc, start):
    assert 0 < arc < 360
    count = tree.count_terminals()
    leaves_distances = (arc / (count - 1))

    angles = {
        tip: start + (leaves_distances * i)
        for i, tip in enumerate(reversed(tree.get_terminals()))
    }

    if tree.root.clades:
        internal_clades_angles(tree.root, angles)

    return angles


def clade_depth(tree):
    depths = tree.depths()

    if not max(depths.values()):
        depths = tree.depths(unit_branch_lengths=True)

    return depths


def draw_label(angle, depth, label, ax):
    rotation = angle + 180 if 270 > angle > 90 else angle
    ha = "right" if 270 > angle > 90 else "left"

    rad = np.deg2rad(angle)

    label = label.split(' ')[0][0] + '.' + ' ' + ' '.join(label.split(' ')[1:])
    ax.text(
        rad,
        depth,
        label,
        rotation=rotation,
        ha=ha,
        va='center', # "center_baseline",
        rotation_mode='anchor',
        style='italic'
    )


def draw_internal_wedge(clade, angles, ax, depth):
    min_angle = min(angles[child]
                    for child in clade.get_terminals())

    max_angle = max(angles[child]
                    for child in clade.get_terminals())

    nnodes = len(clade.get_terminals())
    angles_diff = ((max_angle - min_angle) / (nnodes + 2)) / 2

    min_angle = min_angle - angles_diff
    max_angle = max_angle + angles_diff

    wedge = Wedge(
        (0, 0), depth, min_angle, max_angle, transform=ax.transData._b, **clade.wedge
    )

    ax.add_patch(wedge)

    # Until a better solution is found

    rotation = min_angle + 180 if 270 > min_angle > 90 else min_angle
    ha = "left" if 270 > min_angle > 90 else "right"
    va = "top" if 270 > min_angle > 90 else "bottom"

    rad = np.deg2rad(min_angle)
    ax.text(rad, depth, clade.name, rotation=rotation, ha=ha, va=va, rotation_mode='anchor')


def draw_patch(angle, depth, ax, patch):
    rad = np.deg2rad(angle)
    x_coor = depth * np.cos(rad)
    y_coor = (depth * np.sin(rad))

    patch = patch((x_coor, y_coor))
    patch.set_transform(ax.transData._b)
    patch.set_zorder(3)
    ax.add_patch(patch)


def draw_baseline(node1, node2, ax, lc):
    a1, d1 = node1
    a2, d2 = node2

    # we mesure the number of segments which
    # will be produced
    factor = 1
    ncount = int(abs(a1 - a2) / 5 * factor)
    if ncount < 2: ncount = 2

    angles = np.deg2rad((a1, a2))
    x = np.linspace(angles[0], angles[1], ncount)
    y = interp1d(angles, (d1, d2))(x)
    segs = zip(x, y)

    lc.append(LineCollection([list(segs)], color="black"))


def draw_depthline(angle, depth, cdepth, lc):
    rad = np.deg2rad(angle)
    lc.append(
        LineCollection([[(rad, depth), (rad, cdepth)]], color="black")
    )


def draw_clade(
    clade, ax, angles, depths, lc, root_distance,
    mdepth, label_leaf, patch_leaf, wedge, pad_label,
    pad_patch, pad_wedge
):
    # Recursively draw a tree, down from the given clade
    angle = angles[clade]
    depth = depths[clade] + root_distance

    try:
        patch = clade.patch
    except AttributeError:
        patch = None

    if patch and patch_leaf:
        pdepth = depth + pad_patch
        draw_patch(angle, pdepth, ax, patch)

    if clade.name in label_leaf:
        ldepth = depth + pad_label
        draw_label(angle, ldepth, clade.name.replace('_', ' '), ax)

    try:
        cwedge = clade.wedge
    except AttributeError:
        cwedge = None

    if wedge and cwedge:
        wdepth = mdepth + pad_wedge
        draw_internal_wedge(clade, angles, ax, wdepth)

    for child in clade.clades:
        cangle = angles[child]
        cdepth = depths[child] + root_distance

        # draw lines
        draw_baseline((angle, depth), (cangle, depth), ax, lc)
        draw_depthline(cangle, depth, cdepth, lc)

        draw_clade(child, ax, angles, depths, lc, root_distance,
                   mdepth, label_leaf, patch_leaf, wedge, pad_label,
                   pad_patch, pad_wedge)


def polar_plot(
    tree, label_leaf, ax=None, arc=355, start=0,
    root_distance=.1, patch_leaf=True, wedge=True, pad_label=0.8,
    pad_patch=0, pad_wedge=0, externals=[]
):
    if ax is None:
        fig = plt.figure(figsize=(50, 50), dpi=80)
        ax = fig.add_subplot(polar=True)

    # angles and depths
    angles = clade_angles(tree, arc, start)
    depths = clade_depth(tree)
    mdepth = max(depths.values()) + root_distance

    # setup externals if any
    cdepth = mdepth + mdepth * 0.1

    for external in externals:
        external.set_initial_depth(cdepth)
        external.set_size(mdepth)
        cdepth += external.fsize()

    if not externals:
        usual = mdepth + mdepth * .1
        total_size = max(usual, mdepth + pad_wedge)
    else:
        total_size = cdepth

    ax.set_ylim(0, total_size)
    ax.axis("off")

    # lines collection for faster plotting
    lc = []

    # root depthline
    angle = angles[tree.root]
    draw_depthline(angle, 0, root_distance, lc)

    # draw clades
    draw_clade(tree.root, ax, angles, depths, lc, root_distance,
               mdepth, label_leaf, patch_leaf, wedge, pad_label,
               pad_patch, pad_wedge)

    for element in lc:
        ax.add_collection(element)

    for external in externals:
        external.draw(ax, angles, tree, arc, start)

    return ax