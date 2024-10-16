from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os
from launch.substitutions import ThisLaunchFileDir

def generate_launch_description():
    ROS_NAMESPACE = os.environ['ROS_NAMESPACE'] #<<編集箇所-1

    return LaunchDescription([
        Node(
            package="laser_filters",
            executable="scan_to_scan_filter_chain",
            namespace=ROS_NAMESPACE,
            parameters=[
                PathJoinSubstitution([
                    ThisLaunchFileDir(),
                    "launch", "range_filter_custom.yaml",
                ])],
        )
    ])
