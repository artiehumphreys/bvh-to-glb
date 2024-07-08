import bpy  # type: ignore
import os
import mathutils # type: ignore


def create_sphere_at_bone(bone, armature):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=bone.head_radius, location=bone.head)
    print(bone.tail_radius)
    sphere = bpy.context.object
    sphere.name = f"sphere_{bone.name}"

    mod = sphere.modifiers.new(name="Armature", type="ARMATURE")
    mod.object = armature
    sphere.parent = armature
    sphere.parent_type = "BONE"
    sphere.parent_bone = bone.name


def create_cone_arm(bone, armature):
    parent_tail_world = armature.matrix_world @ bone.parent.head
    bone_head_world = armature.matrix_world @ bone.head

    cone_vector = bone_head_world - parent_tail_world
    cone_length = cone_vector.length
    cone_direction = cone_vector.normalized()

    cone_midpoint_world = (parent_tail_world + bone_head_world) / 2

    bpy.ops.mesh.primitive_cone_add(radius1=bone.head_radius / 1.25, radius2=bone.tail_radius, depth=cone_length, location=cone_midpoint_world)
    cone = bpy.context.object
    cone.name = f"Cone_{bone.parent.name}_to_{bone.name}"

    up_vector = mathutils.Vector((0, 0, 1))
    rotation = cone_direction.to_track_quat('Z', 'Y').to_euler()
    cone.rotation_euler = rotation

    cone.parent = armature
    cone.parent_type = "BONE"
    cone.parent_bone = bone.parent.name


def convert_bvh_to_glb(directory, output_name):
    bpy.ops.wm.read_factory_settings(use_empty=True)

    bpy.ops.wm.obj_import(filepath="Basketball_court.obj")

    for filename in os.listdir(directory):
        if not filename.endswith(".bvh"):
            continue
        bvh_path = os.path.join(directory, filename)
        bpy.ops.import_anim.bvh(filepath=bvh_path)
        bpy.context.scene.render.fps = 60

        armature = bpy.context.object
        if armature.type != "ARMATURE":
            continue
        bpy.context.view_layer.objects.active = armature
        armature.data.display_type = "ENVELOPE"
        armature.data.pose_position = "POSE"
        armature.data.show_bone_colors = True

        for bone in armature.pose.bones:
            print(bone.name)
            create_sphere_at_bone(bone.bone, armature)
            if bone.bone.parent:
                create_cone_arm(bone.bone, armature)

        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="SELECT")

    bpy.ops.export_scene.gltf(filepath=output_name, export_format="GLB")


if __name__ == "__main__":
    convert_bvh_to_glb("output_BVH", "babylon_viewer/output")
