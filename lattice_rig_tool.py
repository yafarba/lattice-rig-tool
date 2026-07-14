import maya.cmds as cmds
import re

# ================================================================================================
# UI CREATION
# Builds the main tool window and collect user settings
# for lattice divisions, control shapes, size and color.
# ================================================================================================

def create_universal_lattice_rig_ui():
    window_id = "universalLatticeRigUI"
    
    if cmds.window(window_id, exists=True):
        cmds.deleteUI(window_id)
        
    cmds.window(window_id, title="Lattice Rig Tool", widthHeight=(320, 340), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=["both", 15])
    cmds.text(label="Universal Lattice Rig Tool", font="boldLabelFont", align="center", height=35)
    
    cmds.text(label="Lattice Divisions (S, T, U):", align="left")
    cmds.rowLayout(numberOfColumns=3, columnWidth3=[80, 80, 80], adjustableColumn=True)
    s_div_field = cmds.intField(value=2, minValue=2, maxValue=20)
    t_div_field = cmds.intField(value=2, minValue=2, maxValue=20)
    u_div_field = cmds.intField(value=2, minValue=2, maxValue=20)
    cmds.setParent("..")
    
    cmds.separator(height=10, style="in")
    
    cmds.text(label="Control Settings:", align="left", font="boldLabelFont")
    
    lbl_w = 60
    field_w = 215
    
    cmds.rowLayout(numberOfColumns=2, columnWidth2=[lbl_w, field_w])
    cmds.text(label="Shape:", align="left", width=lbl_w)
    shape_menu = cmds.optionMenu(width=field_w)
    cmds.menuItem(label="Circle")
    cmds.menuItem(label="Square")
    cmds.menuItem(label="Cube")
    cmds.menuItem(label="Locator")
    cmds.setParent("..")
    
    cmds.rowLayout(numberOfColumns=2, columnWidth2=[lbl_w, field_w])
    cmds.text(label="Size:", align="left", width=lbl_w)
    ctrl_size_field = cmds.floatField(value=0.5, minValue=0.01, maxValue=10.0, precision=2, width=field_w)
    cmds.setParent("..")
    
    cmds.rowLayout(numberOfColumns=2, columnWidth2=[lbl_w, field_w])
    cmds.text(label="Color:", align="left", width=lbl_w)
    color_palette = cmds.colorIndexSliderGrp(
        label="", 
        min=1, 
        max=31, 
        value=18, 
        columnWidth3=[1, 144, 70]
    )
    cmds.setParent("..")
    
    cmds.separator(height=15, style="in")
    
    cmds.button(
        label="Create Lattice Rig", 
        height=40, 
        backgroundColor=[0.25, 0.4, 0.5],
        command=lambda x: generate_lattice_rig_logic(
            s_div_field, t_div_field, u_div_field, 
            ctrl_size_field, color_palette, shape_menu
        )
    )
    
    cmds.showWindow(window_id)
	
# ============================================================================================================
# CONTROL SHAPE CREATION
# Creates the requested controller shape used to drive lattice clusters.
# ============================================================================================================

def create_shape_curves(shape_type, r, name_str):
    if shape_type == "Circle":
        return cmds.circle(nr=(0, 1, 0), r=r, name=name_str)[0]
        
    elif shape_type == "Square":
        d = r
        return cmds.curve(d=1, p=[(-d, 0, -d), (d, 0, -d), (d, 0, d), (-d, 0, d), (-d, 0, -d)], name=name_str)
        
    elif shape_type == "Cube":
        d = r
        cube_points = [
            (-d, d, d), (d, d, d), (d, -d, d), (-d, -d, d), (-d, d, d),
            (-d, d, -d), (d, d, -d), (d, -d, -d), (-d, -d, -d), (-d, d, -d),
            (-d, -d, -d), (-d, -d, d), (d, -d, d), (d, -d, -d), (d, d, -d), (d, d, d)
        ]
        return cmds.curve(d=1, p=cube_points, name=name_str)
        
    elif shape_type == "Locator":
        loc = cmds.spaceLocator(name=name_str)[0]
        for attr in ['localScaleX', 'localScaleY', 'localScaleZ']:
            cmds.setAttr(f"{loc}Shape.{attr}", r)
        return loc
        
    return cmds.circle(nr=(0, 1, 0), r=r, name=name_str)[0]
	
# ========================================================================================================
# NAME MANAGEMENT
# Generates a unique prefix to avoid naming conflicts when
# creating multiple lattice rigs in the same scene.
# ========================================================================================================

def get_unique_prefix(base_prefix):
    if not cmds.objExists(f"{base_prefix}_GRP") and not cmds.objExists(f"{base_prefix}_Lattice"):
        return base_prefix
    
    counter = 1
    while True:
        new_prefix = f"{base_prefix}_{counter}"
        if not cmds.objExists(f"{new_prefix}_GRP") and not cmds.objExists(f"{new_prefix}_Lattice"):
            return new_prefix
        counter += 1

# ========================================================================================================
# OBJECT NAME CLEANUP
# Removes namespaces and unsupported characters to create
# safe node names for generated rig elements.
# ========================================================================================================

def clean_node_name(name):
    short_name = name.split("|")[-1]
    short_name = short_name.split(":")[-1]
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '', short_name)
    
    if not cleaned:
        return "Object"
    return cleaned

# ========================================================================================================
# LATTICE RIG GENERATION
# Creates lattice deformer, cluster per lattice point, animation controls, rig hierarchy structure
# ========================================================================================================

def generate_lattice_rig_logic(s_field, t_field, u_field, size_field, color_palette_ui, shape_menu):
    cmds.undoInfo(openChunk=True)
    
    try:
        div_s = cmds.intField(s_field, query=True, value=True)
        div_t = cmds.intField(t_field, query=True, value=True)
        div_u = cmds.intField(u_field, query=True, value=True)
        ctrl_size = cmds.floatField(size_field, query=True, value=True)
        ctrl_color = cmds.colorIndexSliderGrp(color_palette_ui, query=True, value=True) - 1
        selected_shape = cmds.optionMenu(shape_menu, query=True, value=True)
        
        selection = cmds.ls(sl=True)
        if not selection:
            cmds.warning("Please select your object!")
            cmds.undoInfo(closeChunk=True)
            return
            
        main_target = selection[0]
        
        safe_target_name = clean_node_name(main_target)
        base_prefix = f"Rig_{safe_target_name}"
        prefix = get_unique_prefix(base_prefix)
         
        lattice_nodes = cmds.lattice(selection, divisions=(div_s, div_t, div_u), objectCentered=True, outsideLattice=1)
        lat_trans = cmds.rename(lattice_nodes[1], f"{prefix}_Lattice")
        lat_base = cmds.rename(lattice_nodes[2], f"{prefix}_Base")
        
        main_grp = cmds.group(em=True, name=f"{prefix}_GRP")
        ctrls_grp = cmds.group(em=True, name=f"{prefix}_CTRLS_GRP", parent=main_grp)
        system_grp = cmds.group(em=True, name=f"{prefix}_SYS_GRP", parent=main_grp)
        
        cmds.parent(lat_trans, system_grp)
        cmds.parent(lat_base, system_grp)
        
        obj_rot = cmds.xform(main_target, query=True, rotation=True, worldSpace=True)
        
        counter = 0
        for s in range(div_s):
            for t in range(div_t):
                for u in range(div_u):
                    point_str = f"{lat_trans}.pt[{s}][{t}][{u}]"
                    pos = cmds.pointPosition(point_str, world=True)
                    
                    cluster_nodes = cmds.cluster(point_str, name=f"{prefix}_Clst_{counter}")
                    cluster_handle = cluster_nodes[1]
                    cmds.setAttr(f"{cluster_handle}.visibility", 0)
                    cmds.parent(cluster_handle, system_grp)
                    
                    control_crv = create_shape_curves(selected_shape, ctrl_size, f"{prefix}_CTRL_{counter}")
                    
                    cmds.delete(control_crv, constructionHistory=True)
                    cmds.xform(control_crv, centerPivots=True)
                    
                    control_shapes = cmds.listRelatives(control_crv, shapes=True)
                    if control_shapes:
                        for shape in control_shapes:
                            cmds.setAttr(f"{shape}.overrideEnabled", 1)
                            cmds.setAttr(f"{shape}.overrideColor", ctrl_color)
                    
                    zero_grp = cmds.group(control_crv, name=f"{control_crv}_Zero_GRP")
                    
                    cmds.xform(zero_grp, translation=pos, worldSpace=True)
                    cmds.xform(zero_grp, rotation=obj_rot, worldSpace=True)
                    
                    cmds.makeIdentity(zero_grp, apply=True, t=1, r=1, s=1, n=0, pn=1)
                    cmds.delete(zero_grp, constructionHistory=True)
                    
                    cmds.parent(zero_grp, ctrls_grp)
                    
                    cmds.connectAttr(f"{control_crv}.translate", f"{cluster_handle}.translate")
                    
                    for axis in ['x', 'y', 'z']:
                        cmds.setAttr(f"{control_crv}.r{axis}", lock=True, keyable=False, channelBox=False)
                        cmds.setAttr(f"{control_crv}.s{axis}", lock=True, keyable=False, channelBox=False)
                    
                    counter += 1
                    
    finally:
        cmds.undoInfo(closeChunk=True)

# =============================================================================================
# Launch tool UI
# =============================================================================================

create_universal_lattice_rig_ui()
