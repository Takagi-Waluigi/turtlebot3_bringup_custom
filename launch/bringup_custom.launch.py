import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import ThisLaunchFileDir
from launch_ros.actions import Node

from launch.conditions import IfCondition, UnlessCondition


def generate_launch_description():
    TURTLEBOT3_MODEL = os.environ['TURTLEBOT3_MODEL']
    LDS_MODEL = os.environ['LDS_MODEL']
    LDS_LAUNCH_FILE = '/hlds_laser_custom.launch.py'
    ROS_NAMESPACE = os.environ['ROS_NAMESPACE'] #<<編集箇所-1
    LASER_FILTER_LAUNCH_FILE = '/box_filter_custom.launch.py'

    usb_port = LaunchConfiguration('usb_port', default='/dev/ttyACM0')
    tb3_param_dir = LaunchConfiguration(
        'tb3_param_dir',
        default=os.path.join(
            get_package_share_directory('turtlebot3_bringup_custom'), #<<編集箇所-2
            'params',
            TURTLEBOT3_MODEL + '_' +  ROS_NAMESPACE + '.yaml')) #<<編集箇所-3
    
    if LDS_MODEL == 'LDS-01':
        LDS_LAUNCH_FILE = '/hlds_laser_custom.launch.py'
    elif LDS_MODEL == 'LDS-02':
        LDS_LAUNCH_FILE = '/ld08_custom.launch.py'
    elif LDS_MODEL == 'A1':
        LDS_LAUNCH_FILE = '/sllidar_a1_custom.launch.py'

    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    use_vodom = LaunchConfiguration('use_vodom', default=False)

    use_tracking = LaunchConfiguration('use_tracking', default=False)

    use_sound = LaunchConfiguration('use_sound', default=False)
    
    scan_frame_id = 'base_scan' #<<編集箇所-4

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value=use_sim_time,
            description='Use simulation (Gazebo) clock if true'),

        DeclareLaunchArgument(
            'usb_port',
            default_value=usb_port,
            description='Connected USB port with OpenCR'),

        DeclareLaunchArgument(
            'tb3_param_dir',
            default_value=tb3_param_dir,
            description='Full path to turtlebot3 parameter file to load'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [ThisLaunchFileDir(), '/turtlebot3_state_publisher_custom.launch.py']),
            launch_arguments={'use_sim_time': use_sim_time, 'camera_name': ROS_NAMESPACE}.items(), #<<編集箇所-5
        ),

        IncludeLaunchDescription(
           PythonLaunchDescriptionSource([ThisLaunchFileDir(), '/t265_custom.launch.py']),
           launch_arguments={'use_vodom': use_vodom, 'camera_name': ROS_NAMESPACE}.items(),
           condition=IfCondition(use_vodom),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([ThisLaunchFileDir(), LDS_LAUNCH_FILE]),
            launch_arguments={'port': '/dev/ttyUSB0', 'frame_id': scan_frame_id, 'namespace': ROS_NAMESPACE}.items(), #<<編集箇所-6
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([ThisLaunchFileDir(), LASER_FILTER_LAUNCH_FILE]),
            launch_arguments={'namespace': ROS_NAMESPACE}.items(), #<<編集箇所-6
        ),

        #車輪オドメトリを使用する場合のLaunch
        Node(
            condition=UnlessCondition(use_vodom),
            package='turtlebot3_node',
            executable='turtlebot3_ros',
            namespace=ROS_NAMESPACE, #<<編集箇所-7
            parameters=[tb3_param_dir],
            arguments=['-i', usb_port],
            remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')],
            output='screen'),  
        
        #ビジュアルオドメトリを使用する場合のLaunch
        Node(
            condition=IfCondition(use_vodom),
            package='turtlebot3_node',
            executable='turtlebot3_ros',
            namespace=ROS_NAMESPACE, #<<編集箇所-7
            parameters=[tb3_param_dir,
                        {"odometry.publish_tf":False}],
            arguments=['-i', usb_port],
            output='screen',    
            remappings=[
                ('odom', 'wheel_odom'),
                ('/tf', 'tf'),
                ('/tf_static', 'tf_static')
                ]),       

        Node(
            condition=IfCondition(use_vodom),
            package='odom_converter',
            executable='odom_converter', #<<編集箇所-7
            namespace=ROS_NAMESPACE, #<<編集箇所-7
            output='screen',
            remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]),            

        Node(
            condition=IfCondition(use_tracking),
            package='ros2_realsense_yolo',
            namespace=ROS_NAMESPACE, #<<編集箇所-7
            executable='laser_publisher',
            output='screen'),

        Node(
            condition=IfCondition(use_sound),
            package='play_sound',
            #namespace=ROS_NAMESPACE, #<<編集箇所-7
            executable='play_sound',
            output='screen'),
    ])
