bl_info = {
    "name": "Player Model Quick Loader",
    "author": "GetGrenade",
    "version": (1, 2),
    "blender": (5, 0, 0),
    "location": "View3D > Add > TF2 Player Models",
    "description": "Quickly spawn TF2 player models from a library file",
    "category": "Add Mesh",
}

import bpy
import os

TF2_CLASSES = [
    "scout", "soldier", "pyro", "demo",
    "heavy", "engineer", "medic", "sniper", "spy"
]

class TF2_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    filepath: bpy.props.StringProperty(
        name="TF2 Assets Blend File",
        subtype='FILE_PATH',
        default="tf2_player_models.blend"
    )

    filepath_clean: bpy.props.StringProperty(
        name="TF2 Clean Assets Blend File",
        subtype='FILE_PATH',
        default="tf2_player_models_clean.blend"
    )

    def draw(self, context):
        self.layout.prop(self, "filepath")
        self.layout.prop(self, "filepath_clean")


class OBJECT_OT_spawn_tf2_asset(bpy.types.Operator):
    """Spawn a TF2 asset collection from the library file"""
    bl_idname = "object.spawn_tf2_asset"
    bl_label = "Spawn TF2 Asset"
    bl_options = {'REGISTER', 'UNDO'}

    asset_name: bpy.props.StringProperty()

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        filepath = bpy.path.abspath(prefs.filepath)

        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"File not found: {filepath}")
            return {'CANCELLED'}

        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            if self.asset_name in data_from.collections:
                data_to.collections = [self.asset_name]
            else:
                self.report({'ERROR'}, f"Collection '{self.asset_name}' not found in {filepath}")
                return {'CANCELLED'}

        for coll in data_to.collections:
            if coll is not None:
                context.collection.children.link(coll)

                bpy.ops.object.select_all(action='DESELECT')
                for obj in coll.all_objects:
                    obj.select_set(True)
                    if obj.type == 'ARMATURE':
                        context.view_layer.objects.active = obj

        return {'FINISHED'}





class OBJECT_OT_spawn_all_tf2_stripped(bpy.types.Operator):
    """Spawn all 9 TF2 classes from the clean asset file"""
    bl_idname = "object.spawn_all_tf2_stripped"
    bl_label  = "Spawn All (Stripped)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs    = context.preferences.addons[__name__].preferences
        filepath = bpy.path.abspath(prefs.filepath_clean)

        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"Clean file not found: {filepath}")
            return {'CANCELLED'}

        SPACING = 50.0
        already_present = sum(1 for n in TF2_CLASSES if n in bpy.data.collections)
        slot = already_present
        spawned = []

        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            available = set(data_from.collections)
            data_to.collections = [n for n in TF2_CLASSES
                                    if n in available and n not in bpy.data.collections]

        for coll in data_to.collections:
            if coll is None:
                continue
            context.collection.children.link(coll)
            for obj in coll.all_objects:
                if obj.parent is None:
                    obj.location.x += slot * SPACING
            slot += 1
            spawned.append(coll.name)

        self.report({'INFO'}, f"Spawned {len(spawned)} stripped TF2 models.")
        return {'FINISHED'}


# ── Menus ────────────────────────────────────────────────────────────────────

class VIEW3D_MT_tf2_assets(bpy.types.Menu):
    bl_label = "TF2 Player Models"

    def draw(self, context):
        layout = self.layout

        for asset in TF2_CLASSES:
            op = layout.operator("object.spawn_tf2_asset", text=asset.capitalize())
            op.asset_name = asset

        layout.separator()
        layout.operator(
            "object.spawn_all_tf2_stripped",
            text="Spawn All (Stripped)",
            icon='OUTLINER_OB_ARMATURE',
        )


def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_tf2_assets", icon='OUTLINER_OB_GROUP_INSTANCE')


# ── Register ─────────────────────────────────────────────────────────────────

classes = (
    TF2_AddonPreferences,
    OBJECT_OT_spawn_tf2_asset,
    OBJECT_OT_spawn_all_tf2_stripped,
    VIEW3D_MT_tf2_assets,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
