import bpy  # type: ignore
import os
import mathutils  # type: ignore
from pathlib import Path
import csv
import pandas as pd


class bvh_to_glb:
    def __init__(self, dir="output_BVH", output_path="babylon_viewer/output"):
        self.output_path: str = output_path
        self.filename: str = ""
        self.player_ids: dict[int, str] = {}
        self.teams: dict[str, int] = {}
        self.ball_track: dict[int, tuple] = {}
        self.scale: float = 1.25
        self.dir = dir
        self.start_frame, self.end_frame = 0, 0
        self.process_players(self.dir)
        self.read_ball_csv()

    def get_team(self):
        split = self.filename.split("_")
        return split[1]

    def get_player_name(self):
        split = self.filename.split("_")
        return self.player_ids[int(split[2])]

    def process_players(self, directory):
        for file in os.listdir(directory):
            if not file.endswith(".bvh"):
                continue
            filename = Path(file).stem
            split = filename.split("_")
            if not split[1] in self.teams:
                self.teams[split[1]] = len(self.teams)
            self.player_ids[int(split[2])] = ""
        self.read_player_csv()

    def read_player_csv(self, file=r"players 1.csv"):
        with open(file, mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                player_id = int(row["player_id"])
                if player_id not in self.player_ids:
                    continue
                self.player_ids[player_id] = row["player_name"]

    def read_ball_csv(self, file="Ball_Track.csv"):
        frame = 0
        with open(file, mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.ball_track[frame] = (
                    float(row["X"]),
                    float(row["Y"]),
                    float(row["Z"]),
                )
                frame += 1

    def assign_team_color(self, shape):
        team = self.get_team()
        color = self.teams[team]
        mat = bpy.data.materials.new(name=f"Material_{team}")
        mat.diffuse_color = (color, color, 1, 1)
        shape.data.materials.append(mat)

    def create_sphere_at_bone(self, bone, armature):
        if bone.name == "lWrist" or bone.name == "rWrist":
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=bone.head_radius / self.scale, location=bone.head_local
            )
            sphere = bpy.context.object
            sphere.scale = ((bone.head_local - bone.tail_local).length * 10, 1, 1)
        else:
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=bone.head_radius, location=bone.head_local
            )
        sphere = bpy.context.object
        sphere.name = f"sphere_{bone.name}_{self.filename}"
        if bone.name == "baseHead":
            head_height = 0.15
            sphere.location += mathutils.Vector((0, 0, head_height))
            sphere.scale = (self.scale, self.scale, self.scale)

        mod = sphere.modifiers.new(name="Armature", type="ARMATURE")
        mod.object = armature
        sphere.parent = armature
        sphere.parent_type = "BONE"
        sphere.parent_bone = bone.name
        self.assign_team_color(sphere)

    def create_cone_arm(self, bone, armature):
        parent = bone.parent

        cone_vector = bone.head_local - parent.head_local
        cone_length = cone_vector.length
        cone_direction = cone_vector.normalized()

        cone_midpoint_world = (parent.head_local + bone.head_local) / 2

        bpy.ops.mesh.primitive_cone_add(
            radius1=bone.head_radius / self.scale,
            radius2=bone.tail_radius / self.scale,
            depth=cone_length,
            location=cone_midpoint_world,
        )
        cone = bpy.context.object
        cone.name = f"Cone_{parent.name}_to_{bone.name}_{self.filename}"

        rotation = cone_direction.to_track_quat("Z", "Y").to_euler()
        cone.rotation_euler = rotation

        cone.parent = armature
        cone.parent_type = "BONE"
        cone.parent_bone = parent.name
        self.assign_team_color(cone)

    def display_name(self, armature):
        z_constant = 0.1
        player_name = self.get_player_name()
        bpy.ops.object.select_all(action="DESELECT")

        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, z_constant))
        empty_obj = bpy.context.active_object
        empty_obj.name = "empty"

        bpy.ops.object.text_add(
            location=(0, 0, z_constant), radius=0.6, rotation=(0, 0, 1.5708)
        )
        text_obj = bpy.context.active_object
        text_obj.name = "text"
        text_obj.data.body = player_name

        text_obj.data.align_x = "CENTER"
        text_obj.data.materials.clear()
        material = bpy.data.materials.new(name="font color")
        material.diffuse_color = (0, 0, 0, 1)
        text_obj.data.materials.append(material)

        text_obj.parent = empty_obj

        pelvis_bone = armature.pose.bones["pelvis"]
        constraint = empty_obj.constraints.new("COPY_LOCATION")
        constraint.target = armature
        constraint.subtarget = pelvis_bone.name
        constraint.head_tail = 0.0

        constraint.influence = 1.0

        for frame in range(self.start_frame, self.end_frame + 1):
            bpy.context.scene.frame_set(frame)
            empty_obj.location = pelvis_bone.matrix.translation
            empty_obj.keyframe_insert(data_path="location", index=-1)

            text_world_matrix = text_obj.matrix_world.copy()
            text_world_matrix.translation.z = z_constant
            text_obj.matrix_world = text_world_matrix
            pelvis_world_x = pelvis_bone.matrix.translation.x
            if pelvis_world_x != 0:
                text_obj.location.x = -1 * pelvis_world_x / abs(pelvis_world_x)
                text_obj.rotation_euler[2] = -1.5708 * (
                    pelvis_world_x / abs(pelvis_world_x)
                )
            else:
                text_obj.location.x = 1
                text_obj.rotation_euler[2] = 1.5708

            text_obj.keyframe_insert(data_path="location", index=-1)
            text_obj.keyframe_insert(data_path="rotation_euler", index=2)

    def display_ball(self):
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.124, location=(0, 0, 0))
        ball_obj = bpy.context.active_object
        ball_obj.name = "ball"
        ball_obj.data.materials.clear()
        material = bpy.data.materials.new(name="ball color")
        material.diffuse_color = (1, 0.3, 0.1, 1)
        ball_obj.data.materials.append(material)

        for frame in range(self.start_frame, self.end_frame):
            bpy.context.scene.frame_set(frame)
            ball_obj.location = self.ball_track[frame]
            ball_obj.keyframe_insert(data_path="location", index=-1)

    def convert_bvh_to_glb(self, output_name):
        display_ball = False
        bpy.ops.wm.read_factory_settings(use_empty=True)

        bpy.ops.wm.obj_import(filepath="court.obj")

        for file in os.listdir(self.dir):
            if not file.endswith(".bvh"):
                continue
            self.filename = Path(file).stem

            bvh_path = os.path.join(self.dir, file)
            bpy.ops.import_anim.bvh(filepath=bvh_path)
            bpy.context.scene.render.fps = 60

            armature = bpy.context.object
            if armature.type != "ARMATURE":
                continue
            bpy.context.view_layer.objects.active = armature

            action = armature.animation_data.action
            if not action:
                print("Error getting frame range. Try manually inputting it")
                exit(1)
            self.start_frame = int(action.frame_range[0])
            self.end_frame = int(action.frame_range[1])

            if not display_ball:
                self.display_ball()
                display_ball = True

            for bone in armature.pose.bones:
                bone.bone.use_local_location = True
                bone.bone.use_relative_parent = True
                self.create_sphere_at_bone(bone.bone, armature)
                if bone.bone.parent:
                    self.create_cone_arm(bone.bone, armature)
                if bone.name == "pelvis":
                    self.display_name(armature)

        bpy.ops.object.select_all(action="SELECT")

        bpy.ops.export_scene.gltf(filepath=output_name, export_format="GLB")


if __name__ == "__main__":
    converter = bvh_to_glb()
    converter.convert_bvh_to_glb(converter.output_path)
