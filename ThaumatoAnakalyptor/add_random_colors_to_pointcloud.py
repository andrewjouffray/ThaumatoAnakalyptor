### Julian Schilliger - ThaumatoAnakalyptor - Vesuvius Challenge 2023

import os
import random
import open3d as o3d
import numpy as np
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from threading import current_thread

def load_ply(filename):
    """
    Load point cloud data from a .ply file.
    """
    # Check that the file exists
    assert os.path.isfile(filename), f"File {filename} not found."
    print(f"File {filename} found.")

    # Load the file and extract the points and normals
    pcd = o3d.io.read_point_cloud(filename)
    points = np.asarray(pcd.points)
    normals = np.asarray(pcd.normals)

    print(f"Loaded {len(points)} points and normals from {filename}.")
    return points, normals

def save_surface_ply(surface_points, normals, filename):
    # Ensure random colors aren't repeated due to thread-local random state.
    # Seed with the thread's identifier, process id and number of points.
    np.random.seed((len(surface_points) * int((os.getpid() << 16) | (id(current_thread()) & 0xFFFF)))% (2**31))
    print(f"Saving {len(surface_points)} points to {filename}...")

    # Create an Open3D point cloud object and populate it
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(surface_points)
    pcd.normals = o3d.utility.Vector3dVector(normals)
    # random colors
    pcd.colors = o3d.utility.Vector3dVector(np.random.uniform(0, 1, size=(surface_points.shape[0], 3)))

    # Create folder if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    print(f"Made folder {os.path.dirname(filename)} if it didn't exist.")

    # Save as a PLY file
    o3d.io.write_point_cloud(filename, pcd)
    print(f"Saved {filename}.")

def process_file(file, src_folder, dest_folder):
    # Load volume
    points, normals = load_ply(os.path.join(src_folder, file))
    # Save volume
    save_surface_ply(points, normals, os.path.join(dest_folder, file))


def add_random_colors(src_folder, dest_folder):
    # List all files in the source folder
    all_files = os.listdir(src_folder)
    print("Listing all files in the source folder...")

    # Filter out all files that are not .ply files
    ply_files = [file for file in all_files if file.endswith('.ply')]
    
    print(f"Found {len(ply_files)} .ply files in {src_folder}")
    # Make destination folder if it does not exist
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    print(f"Processing {len(ply_files)} files...")
    # Use ThreadPoolExecutor to process files in parallel
    with ProcessPoolExecutor(1) as executor:
        list(tqdm(executor.map(process_file, ply_files, [src_folder]*len(ply_files), [dest_folder]*len(ply_files)), total=len(ply_files)))


if __name__ == '__main__':
    # Sample usage:
    src_folder = '/media/julian/SSD2/scroll3_surface_points/point_cloud_recto'  # Replace with your source folder path
    dest_folder = '/media/julian/SSD2/scroll3_surface_points/point_cloud_colorized_recto'  # Replace with your destination folder path

    add_random_colors(src_folder, dest_folder)