"""
3D Master Vault — Blender 5.3 Headless Production Starter Script
Run:
  "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe" -b --factory-startup -P "Blender 5.3 Headless Starter Script.py" -- --out-dir ./build
"""

import argparse
import math
import pathlib
import sys
import bpy
from mathutils import Vector


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.0
    return scene


def configure_cycles(scene, samples=64, width=1024, height=1024):
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.02
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.cycles.max_bounces = 8
    scene.cycles.sample_clamp_indirect = 10.0
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.image_settings.file_format = 'PNG'

    # Auto-enable GPU if available
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for dev_type in ('OPTIX', 'CUDA', 'HIP', 'ONEAPI'):
            prefs.compute_device_type = dev_type
            prefs.get_devices()
            if any(d.type == dev_type for d in prefs.devices):
                for d in prefs.devices:
                    d.use = (d.type == dev_type)
                scene.cycles.device = 'GPU'
                break
    except Exception:
        scene.cycles.device = 'CPU'


def ground_and_freeze(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    cx = 0.5 * (min(v.x for v in bbox) + max(v.x for v in bbox))
    cy = 0.5 * (min(v.y for v in bbox) + max(v.y for v in bbox))
    min_z = min(v.z for v in bbox)
    obj.location.x -= cx
    obj.location.y -= cy
    obj.location.z -= min_z
    bpy.context.view_layer.update()
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')


def add_three_point_rig(target=(0.0, 0.0, 0.5), radius=2.5):
    def add_area(name, loc, energy, size, color, spread_deg=80):
        ld = bpy.data.lights.new(name=name, type='AREA')
        ld.energy = energy
        ld.size = size
        ld.color = color
        ld.spread = math.radians(spread_deg)
        ob = bpy.data.objects.new(name=name, object_data=ld)
        bpy.context.collection.objects.link(ob)
        ob.location = loc
        ob.rotation_euler = (Vector(target) - ob.location).to_track_quat('-Z', 'Y').to_euler()
        return ob

    add_area("Key",  ( radius * 0.9, -radius * 0.85, radius * 0.95), 180, 1.2, (1.0, 0.94, 0.86), 75)
    add_area("Fill", (-radius * 1.1, -radius * 0.60, radius * 0.60),  55, 2.4, (0.76, 0.86, 1.0), 110)
    add_area("Rim",  (-radius * 0.75, radius * 0.95, radius * 1.00), 220, 0.6, (0.95, 0.98, 1.0), 55)


def render_three_angles(scene, cam, hero_objs, out_dir: pathlib.Path):
    coords = []
    for ob in hero_objs:
        coords.extend([ob.matrix_world @ Vector(c) for c in ob.bound_box])
    bmin = Vector((min(v.x for v in coords), min(v.y for v in coords), min(v.z for v in coords)))
    bmax = Vector((max(v.x for v in coords), max(v.y for v in coords), max(v.z for v in coords)))
    center = 0.5 * (bmin + bmax)
    radius = max(0.05, (bmax - bmin).length * 0.5)

    shots = [
        ("01_hero_3q.png", 35.0, 18.0, 65.0, 0.72),
        ("02_side_silhouette.png", 90.0, 8.0, 65.0, 0.72),
        ("03_closeup_detail.png", 25.0, 14.0, 85.0, 1.15),
    ]
    for fname, yaw_deg, pitch_deg, lens, fill in shots:
        cam.data.lens = lens
        dist = (radius / math.sin(cam.data.angle_y * 0.5)) / fill
        yaw, pitch = math.radians(yaw_deg), math.radians(pitch_deg)
        cam.location = center + Vector((
            dist * math.cos(pitch) * math.sin(yaw),
            -dist * math.cos(pitch) * math.cos(yaw),
            dist * math.sin(pitch),
        ))
        cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(out_dir / fname)
        bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="./build")
    args = parser.parse_args(argv)
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scene = reset_scene()
    configure_cycles(scene, samples=48, width=960, height=960)

    # Example beveled studio hero cube (replace with your asset builder!)
    bpy.ops.mesh.primitive_cube_add(size=0.4)
    hero = bpy.context.active_object
    hero.name = "HeroAsset"
    bev = hero.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.015
    bev.segments = 3
    bpy.ops.object.shade_smooth()
    ground_and_freeze(hero)

    # Studio shadow catcher floor
    bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "StudioFloor"

    add_three_point_rig(target=(0, 0, 0.2), radius=2.0)

    cam_data = bpy.data.cameras.new("MainCam")
    cam = bpy.data.objects.new("MainCam", cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam

    # Export clean GLB
    bpy.ops.object.select_all(action='DESELECT')
    hero.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(out_dir / "hero.glb"),
        export_format='GLB',
        use_selection=True,
        export_yup=True,
        export_apply=True,
    )
    render_three_angles(scene, cam, [hero], out_dir)
    bpy.ops.wm.save_as_mainfile(filepath=str(out_dir / "scene.blend"))


if __name__ == "__main__":
    main()
