bl_info = {
    "name": "Player Model Quick Loader",
    "author": "GetGrenade",
    "version": (1, 1),
    "blender": (5, 0, 0),
    "location": "View3D > Add > TF2 Player Models",
    "description": "Quickly spawn TF2 player models from a library file",
    "category": "Add Mesh",
}

import bpy
import os

class TF2_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    filepath: bpy.props.StringProperty(
        name="TF2 Assets Blend File",
        subtype='FILE_PATH',
        default="tf2_player_models.blend"
    )

    def draw(self, context):
        self.layout.prop(self, "filepath")

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

        # We look for COLLECTIONS this time
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            if self.asset_name in data_from.collections:
                data_to.collections = [self.asset_name]
            else:
                self.report({'ERROR'}, f"Collection '{self.asset_name}' not found in {filepath}")
                return {'CANCELLED'}

        # Link the collection to the current scene's collection
        for coll in data_to.collections:
            if coll is not None:
                context.collection.children.link(coll)
                
                # Optional: Select the objects inside the new collection
                bpy.ops.object.select_all(action='DESELECT')
                for obj in coll.all_objects:
                    obj.select_set(True)
                    if obj.type == 'ARMATURE':
                        context.view_layer.objects.active = obj
        
        return {'FINISHED'}

class VIEW3D_MT_tf2_assets(bpy.types.Menu):
    bl_label = "TF2 Player Models"

    def draw(self, context):
        layout = self.layout
        # Ensure these names match your Collection names exactly (case-sensitive)
        assets = [
            "demo", "engineer", "heavy", "medic", 
            "pyro", "scout", "sniper", "soldier", "spy"
        ]
        
        for asset in assets:
            op = layout.operator("object.spawn_tf2_asset", text=asset.capitalize())
            op.asset_name = asset

def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_tf2_assets", icon='OUTLINER_OB_GROUP_INSTANCE')

classes = (
    TF2_AddonPreferences,
    OBJECT_OT_spawn_tf2_asset,
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