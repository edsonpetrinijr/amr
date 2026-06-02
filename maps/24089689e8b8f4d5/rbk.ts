﻿Laser-odom calibration using laser ~-~ 使用激光里程计进行激光标定
Read model params as the CalibrationTask plugin started ~-~ 在 CalibrationTask 插件启动时读取模型参数
Particle move radius (mm) ~-~ 原地旋转粒子扩散范围(mm)
The map points in current slam region is using by SLAM ~-~ 是否扣除SLAM定位区域激光点不用于建图
Record debug info of MCLoc mode ~-~ 记录定位状态调试信息
The time interval of recording localization info (s) ~-~ 定位信息记录间隔(s)
The distance threshold of recovering in normal mode without using skiding mode (m) ~-~ 运动距离，单位m（恢复定位不启用打滑检测）
The angle threshold of recovering in normal mode without using skiding mode (degree) ~-~ 运动角度，单位度（恢复定位不启用打滑检测）
Check if force extra move ~-~ 是否强制扩散
The distance of force extra move (mm) ~-~ 强制扩散距离 mm
The angle of force extra move (degree) ~-~ 强制扩散角度 度
The type of reflector: Type = 0--circle,Type = 1--plane ~-~ 反光板型号：Type = 0--圆，Type = 1--平面
The minimum number of detecting reflector in map ~-~ 地图拟合反光板最少需要反光点数量
The width or diameter of reflector ~-~ 反光板宽度或直径
use laser rssi to calculate center  ~-~ 使用Rssi加权平均求中心点
The mininum number of clustering reflector points ~-~ 反光板点聚类阈值
The number of laser beams used in Localization ~-~ 定位激光使用数量
The time threshold in receiving laser scan by localization(ms) ~-~ 定位模块丢失激光时间阈值(ms)
The time threshold in receiving odometer by localization(ms) ~-~ 定位模块丢失里程时间阈值(ms)
The rssi threshold of detecting reflector ~-~ 反光板的反射率
The increment of RSSI ~-~ 反射率增加值
Set error if not enough reflectors can be detected ~-~ 反光板数量不足时报错
The distance threshold of setting error if tag cannot be seen ~-~ 二维码定位偏离路线报警距离
Time delay ~-~ 时延
Sleep time ~-~ 线程延时
The time interval of recovering after stop caused by skidding ~-~ 打滑静止后恢复时间

The particle move radius in low speed ~-~ 低速粒子扩散距离范围
The particle move radius in low speed ~-~ 低速粒子扩散角度范围
The number of particles in localization ~-~ 定位粒子数
The maximum num of particles in relocalization ~-~ 重定位最大粒子数
The confidence threshold to change into odometer mode ~-~ 纯里程模式阈值
The confidence threshold to change into reflector mode ~-~ 使用反光板定位阈值
Stop use particle filter localization if stop from odometer ~-~ 里程停止时不定位
Grid size ~-~ 栅格化大小
The number of thread used by particle filter localization ~-~ 定位线程数
Stop use particle filter localization if stop from odometer ~-~ 里程停止时不定位

Max Speed ​​(m/s) ~-~ 最大速度(m/s)
Maximum reverse speed (m/s) ~-~ 最大倒退速度(m/s)
Max acceleration (m/s^2) ~-~ 最大加速度(m/s^2)
Maximum Deceleration (m/s^2) ~-~ 最大减速度(m/s^2)
Maximum manual acceleration (m/s^2) ~-~ 最大手动加速度(m/s^2)
Max manual deceleration (m/s^2) ~-~ 最大手动减速度(m/s^2)
Maximum rotation speed (°/s) ~-~ 最大转速度(°/s)
Maximum rotation acceleration (°/s^2) ~-~ 最大转加速度(°/s^2)
Maximum rotation speed (°/s^2) ~-~ 最大转减速度(°/s^2)
Max manual rotation acceleration (°/s^2) ~-~ 最大手动转加速度(°/s^2)
Maximum manual rotation speed (°/s^2) ~-~ 最大手动转减速度(°/s^2)
The maximum distance the robot deviates from the line (m) ~-~ 机器人偏离线路的最大距离(m)
Whether the robot alarms outside the line ~-~ 机器人在线路外是否进行报警
Load maximum speed (m/s) ~-~ 载货时的最大速度(m/s)
Load maximum reverse speed (m/s) ~-~ 载货时的最大倒退速度(m/s)
Load maximum acceleration (m/s^2) ~-~ 载货时的最大加速度(m/s^2)
Load maximum deceleration (m/s^2) ~-~ 载货时的最大减速度(m/s^2)
Load maximum manual acceleration (m/s^2) ~-~ 载货时的最大手动加速度(m/s^2)
Load maximum manual deceleration (m/s^2) ~-~ 载货时的最大手动减速度(m/s^2)
Load maximum rotation speed (°/s) ~-~ 载货时的最大转速度(°/s)
Load maximum rotation acceleration (°/s^2) ~-~ 载货时的最大转加速度(°/s^2)
Load maximum rotation speed (°/s^2) ~-~ 载货时的最大转减速度(°/s^2)
Load maximum manual rotation acceleration (°/s^2) ~-~ 载货时的最大手动转加速度(°/s^2)
Load maximum manual rotation speed (°/s^2) ~-~ 载货时的最大手动转减速度(°/s^2)
Mid-point-to-point distance accuracy (m) ~-~ 中间点到点距离精度(m)
Go Angle(°) ~-~ 起步朝向(°)
Turn Maximum Addition Factor ~-~ 转弯最大加系数
Turning angular acceleration coefficient ~-~ 转弯角加速度系数
Estimated turning offset distance (m) ~-~ 转弯偏移预估距离(m)
Motion Planning Parameters ~-~ 运动规划参数
Bending Delay(s) ~-~ 弯曲延时(s)
Emergency Stop Distance (m) ~-~ 紧急停止距离(m)
Charge leaving open loop linear motion time(s) ~-~ 充电离开开环直线运动时间(s)
The identified path uses pure mileage mode (forklift) ~-~ 识别后的路径采用纯里程模式(叉车)
The identified path uses pure mileage mode (non-forklift) ~-~ 识别后的路径采用纯里程模式(非叉车)
Use lqr mode to follow ~-~ 采用lqr模式跟随
Max Speed ​​(m/s) ~-~ 最大速度(m/s)
Max Back Speed ​​(m/s) ~-~ 最大倒退速度(m/s)
Max acceleration (m/s^2) ~-~ 最大加速度(m/s^2)
Maximum Deceleration (m/s^2) ~-~ 最大减速度(m/s^2)
Max manual acceleration (m/s^2) ~-~ 最大手动加速度(m/s^2)
Maximum manual deceleration (m/s^2) ~-~ 最大手动减速度(m/s^2)
Maximum rotation speed (°/s) ~-~ 最大转速度(°/s)
Maximum rotation acceleration (°/s^2) ~-~ 最大转加速度(°/s^2)
Maximum rotation speed (°/s^2) ~-~ 最大转减速度(°/s^2)
Max manual rotation acceleration (°/s^2) ~-~ 最大手动转加速度(°/s^2)
Maximum manual rotation speed (°/s^2) ~-~ 最大手动转减速度(°/s^2)
Motion Planning Parameters ~-~ 运动规划参数
Load maximum speed (m/s) ~-~ Load最大速度(m/s)
Load maximum reverse speed (m/s) ~-~ Load最大倒退速度(m/s)
Load maximum acceleration (m/s^2) ~-~ Load最大加速度(m/s^2)
Load maximum deceleration (m/s^2) ~-~ Load最大减速度(m/s^2)
Load maximum manual acceleration (m/s^2) ~-~ Load最大手动加速度(m/s^2)
Load maximum manual deceleration (m/s^2) ~-~ Load最大手动减速度(m/s^2)
Load maximum rotation speed (°/s) ~-~ Load最大转速度(°/s)
Load maximum rotation acceleration (°/s^2) ~-~ Load最大转加速度(°/s^2)
Load maximum rotation speed (°/s^2) ~-~ Load最大转减速度(°/s^2)
Load maximum manual rotation acceleration (°/s^2) ~-~ Load最大手动转加速度(°/s^2)
Load maximum manual rotation speed (°/s^2) ~-~ Load最大手动转减速度(°/s^2)
Charge leaving open loop linear motion time(s) ~-~ 充电离开开环直线运动时间(s)
The identified path uses pure mileage mode (forklift) ~-~ 识别后的路径采用纯里程模式(叉车)
Max Speed ​​(m/s) ~-~ 最大速度(m/s)
Maximum reverse speed (m/s) ~-~ 最大倒退速度(m/s)
Maximum acceleration (m/s^2) ~-~ 最大加速度(m/s^2)
Maximum Deceleration (m/s^2) ~-~ 最大减速度(m/s^2)
Max manual acceleration (m/s^2) ~-~ 最大手动加速度(m/s^2)
Maximum manual deceleration (m/s^2) ~-~ 最大手动减速度(m/s^2)
Maximum rotation speed (°/s) ~-~ 最大转速度(°/s)
Maximum rotation acceleration (°/s^2) ~-~ 最大转加速度(°/s^2)
Maximum rotation deceleration (°/s^2) ~-~ 最大转减速度(°/s^2)
Max manual rotation acceleration (°/s^2) ~-~ 最大手动转加速度(°/s^2)
Maximum manual rotation speed (°/s^2) ~-~ 最大手动转减速度(°/s^2)
Motion Planning Parameters ~-~ 运动规划参数
Load maximum speed (m/s) ~-~ Load最大速度(m/s)
Load maximum reverse speed (m/s) ~-~ Load最大倒退速度(m/s)
Load maximum acceleration (m/s^2) ~-~ Load最大加速度(m/s^2)
Load maximum deceleration (m/s^2) ~-~ Load最大减速度(m/s^2)
Load maximum manual acceleration (m/s^2) ~-~ Load最大手动加速度(m/s^2)
Load maximum manual deceleration (m/s^2) ~-~ Load最大手动减速度(m/s^2)
Load maximum rotation speed (°/s) ~-~ Load最大转速度(°/s)
Load maximum rotation acceleration (°/s^2) ~-~ Load最大转加速度(°/s^2)
Load maximum rotation speed (°/s^2) ~-~ Load最大转减速度(°/s^2)
Load maximum manual rotation acceleration (°/s^2) ~-~ Load最大手动转加速度(°/s^2)
Load maximum manual rotation speed (°/s^2) ~-~ Load最大手动转减速度(°/s^2)
Charge leaving open loop linear motion time(s) ~-~ 充电离开开环直线运动时间(s)
The identified path uses pure mileage mode (non-forklift) ~-~ 识别后的路径采用纯里程模式(非叉车)
The maximum distance the robot deviates from the line (m) ~-~ 机器人偏离线路的最大距离(m)
Whether the robot alarms outside the line ~-~ 机器人在线路外是否进行报警
Mid-point-to-point distance accuracy (m) ~-~ 中间点到点距离精度(m)
Go Angle(°) ~-~ Go Angle(°)
Maximum Turning Addition Factor ~-~ 转弯最大加系数
Turning angular acceleration coefficient ~-~ 转弯角加速度系数
Estimated turning offset distance (m) ~-~ 转弯偏移预估距离(m)
Bending Delay(s) ~-~ 弯曲延时(s)
Emergency Stop Distance (m) ~-~ 紧急停止距离(m)
Use lqr mode to follow ~-~ 采用lqr模式跟随
Maximum tray rotation angular velocity (°/s) ~-~ 最大托盘旋转角速度(°/s)
Maximum tray rotation angular acceleration (°/s^2) ~-~ 最大托盘旋转角加速度(°/s^2)
Maximum pallet rotation angle deceleration (°/s^2) ~-~ 最大托盘旋转角减速度(°/s^2)
Distance to point accuracy (m) ~-~ 到点距离精度(m)
ReachAngle(°) ~-~ 到点角度(°)
emergency stop deceleration (m/s^2), if less than 0, emergency stop ~-~ 急停减速度(m/s^2), 小于0则急停
Emergency stop deceleration speed (°/s^2), if it is less than 0 then emergency stop ~-~ 急停减角速度(°/s^2), 小于0则急停
Max acceleration Jerk(m/s^3) ~-~ 最大加速度Jerk(m/s^3)
Maximum acceleration step Jerk(m/s^4) ~-~ 最大加速度步长Jerk(m/s^4)
Maximum rotational acceleration Jerk(°/s^3) ~-~ 最大转加速度Jerk(°/s^3)
Turn Angle(°) ~-~ 认定线路不相切的角度阈值(°)
Whether the navigation uses ultrasound ~-~ 导航是否使用超声
Whether the navigation uses laser to stop obstacles ~-~ 导航是否使用激光停障
Whether the navigation uses a distance measuring sensor ~-~ 导航是否使用测距传感器
Whether the navigation uses virtual laser points ~-~ 导航是否使用虚拟激光点
Whether the navigation uses an anti-fall sensor ~-~ 导航是否使用防跌落传感器
Whether the navigation uses infrared sensors ~-~ 导航是否使用红外传感器
Whether the navigation uses a 3D camera to detect raised obstacles ~-~ 导航是否使用3D相机检测凸起障碍物
Whether the navigation uses a 3D camera to detect potholes ~-~ 导航是否使用3D相机检测坑洞
Collision prediction distance (m) ~-~ 碰撞预测的距离(m)
Deceleration prediction distance (m) ~-~ 减速预测的距离(m)
Deceleration Speed ​​(m/s) ~-~ 减速速度(m/s)
Collision prediction robot expansion width (m) ~-~ 碰撞预测的机器人扩展宽度(m)
Robot expansion width for deceleration collision prediction (m) ~-~ 减速碰撞预测的机器人扩展宽度(m)
Obstacle bypass: a few seconds after being blocked, start bypassing(s) ~-~ 绕障：被阻挡后几秒开始绕行(s)
execution cycle (ms) ~-~ 执行周期(ms)
Whether to enable the stop function in manual mode ~-~ 是否开启手动模式下的停障功能
Extra stay time after the end of the block (s) ~-~ 阻挡结束后额外的停留时间(s)
Alarm(s) will start after being blocked (s) ~-~ 被阻挡后几秒后开始报警(s)
Whether to alarm after being blocked ~-~ 被阻挡后是否报警
The nearest station distance threshold (m) ~-~ 最近站点距离阈值(m)
Debug output switch ~-~ 调试输出开关
Global default path width (m), 0 means not considering path width ~-~ 全局默认路径宽度(m)，0 为不考虑路径宽度
Robot replanning task distance threshold (m) ~-~ 机器人重新规划任务的距离阈值(m)
Robot replanning task angle threshold (°) ~-~ 机器人重新规划任务的角度阈值(°)
To-point accuracy alarm distance threshold (m) ~-~ 到点精度报警距离阈值(m)
To-point accuracy alarm angle threshold (°) ~-~ 到点精度报警角度阈值(°)
Slowdown distance in manual mode (m) ~-~ 手动模式下减速距离(m)
Stop distance in manual mode (m) ~-~ 手动模式下停止距离(m)
Stop angle threshold in manual mode (°) ~-~ 手动模式下停止角度阈值(°)
Cutting area debugging switch ~-~ 抠除区域调试开关
Maximum number of recognitions, -1 means always recognizing ~-~ 最多识别次数,-1表示一直在识别
Collision Points Threshold Number ~-~ 进行碰撞检测的激光点个数阈值
SmartRotation ~-~ 智能转向
Accuracy when selecting a route ~-~ 选择线路的时的精度
ForWardDist (m) ~-~ 到点二次调整前置距离 (m)
Recognize path speed (m/s) ~-~ 识别路径速度(m/s)
Recognition planning lead distance (m) ~-~ 识别规划前置距离(m)
Recognition planning initial minimum lead distance, less than 0 do not enable (m) ~-~ 识别规划初始最小前置距离,小于0不启用(m)
Back distance after identification point (m) ~-~ 识别点后的后退距离(m)
The maximum deviation distance between the recognition result and the point position (m) ~-~ 识别结果和点位最大偏离距离(m)
Adjust orientation before awareness ~-~ 识前调整朝向
Load collision prediction distance (m) ~-~ 载货时碰撞预测的距离(m)
Load deceleration prediction distance (m) ~-~ 载货时减速预测的距离(m)
Load collision prediction robot expansion width (m) ~-~ 载货时碰撞预测的机器人扩展宽度(m)
Load deceleration collision prediction robot expansion width (m) ~-~ 载货时减速碰撞预测的机器人扩展宽度(m)
Load emergency stop deceleration (m/s^2), if it is less than 0 then emergency stop ~-~ 载货时的急停减速度(m/s^2), 小于0则急停
Load emergency stop deceleration speed (°/s^2), less than 0 then emergency stop ~-~ 载货时的急停减角速度(°/s^2), 小于0则急停
Minimum rudder angle resolution (degrees) ~-~ 最小舵角分辨率(度)
Override recognition height, less than 0 do not enable (m) ~-~ 覆盖识别高度，小于 0 不启用(m)
After the forklift picks up the goods, the extra lift height of the fork (m) ~-~ 叉车取货物后，货叉额外抬升的高度(m)
Waiting time before recognition ~-~ 识别前等待的时间
Forklift recognition, the height of the fork (m) ~-~ 叉车识别时，货叉的高度(m)
The height of the fork (m) ~-~ 叉车识别时，货叉的高度(m)
Recognition path speed (m/s) ~-~ 识别路径速度(m/s)
Recognition planning lead distance (m) ~-~ 识别规划前置距离(m)
Recognition planning initial minimum lead distance, less than 0 do not enable (m) ~-~ 识别规划初始最小前置距离,小于0不启用(m)
PGV Rec Times ~-~ PGV 看不到二维码报警的次数阈值
PGV Speed ~-~ 按 PGV 进行二次调整时的移动速度(m/s)
PGV Rot Speed ~-~ 按 PGV 进行二次调整时的角速度(degree/s)
PGV Reach Dist (m) ~-~ PGV 首次调整的位置到点精度(m)
PGV Reach Angle (degree) ~-~ PGV 首次调整的角度到点精度(degree)
PGV Reach Dist calibration tolerance (m)  ~-~ PGV 非首次调整的额外的位置到点精度(m)
PGV Reach Angle calibration tolerance (degree) ~-~ PGV 非首次调整的额外的角度到点精度(degree)
PGV did not see whether the QR code reported an error ~-~ PGV没有看到二维码是否报错
PGV filter parameter threshold ~-~ PGV滤波参数阈值
Automatically reset to zero when the non-spin-up tray is lifted ~-~ 非随动顶升托盘顶升状态下自动归零
Automatically reset to zero when the non-spin-up tray is not lifted ~-~ 非随动顶升托盘非顶升状态下自动归零
Simulation time(s) ~-~ 仿真时间(s)
Simulation time step (s) ~-~ 仿真时间步长(s)
Judging the time required for the robot to stand still (s) ~-~ 判断机器人静止所需的时间(s)
How far away from the line to start re-planning ~-~ 偏离线路多远开始重新规划
Following Kp ~-~ 随动Kp
SpinKd ~-~ 随动Kd
SpinKi ~-~ 随动Ki
Follow-up reference angular velocity threshold ~-~ 随动参考角速度阈值
Minimum Turntable Speed ~-~ 最小转盘转速
When the angle of the tray and the target angle are less than this threshold, complete (°) ~-~ 当托盘的角度和目标角度小于此阈值，则完成（°）
When the angle of the pallet and the angle required to start is less than this threshold, it is complete (°) ~-~ 当托盘的角度和起步所需角度小于此阈值，则完成（°）
When the angle of the tray and the target angle are greater than this threshold, an error (°) ~-~ 当托盘的角度和目标角度大于此阈值，则报错（°）
tray deviation from error threshold ~-~ 托盘偏离报错阈值
Curvature Average Range ~-~ 曲率平均范围
PGV adjust maximum angle ~-~ PGV调整最大角度
Detection distance of obstacles at the end point (m) ~-~ 终点处障碍物检测距离(m)
Distance threshold for judging whether it is a dynamic obstacle ~-~ 判别是否是动态障碍物的距离阈值
LD_LOG status,...2:info,3:run, 4:warn... ~-~ LD_LOG状态，...2:info,3:run, 4:warn...
The distance between the regression point and adjacent obstacles ~-~ 回归点与相邻障碍物的距离
Re-plan the route under exercise ~-~ 运动下重新规划线路
Fork Di effective distance (m), effective at any position less than 0 ~-~ 货叉Di起效距离(m)，小于0任何位置都起效
Return using recognized path ~-~ 采用识别的路径返回
Whether to follow in the non-lifting state ~-~ 在非顶升状态下是否随动
VKp value of patrol PID ~-~ 巡线PID 的 vKp 值
VKd value of patrol PID ~-~ 巡线PID 的 vKd 值
WKp value of line patrol PID ~-~ 巡线PID 的 wKp 值
WKd value of line patrol PID ~-~ 巡线PID 的 wKd 值
Line patrol forward and lateral system error m ~-~ 巡线向前侧向系统误差m
Line patrol backward walking lateral system error m ~-~ 巡线倒走侧向系统误差m
Recognize and generate a single path ReshapeRatio ~-~ 识别生成单条路径ReshapeRatio
Identify the starting angle accuracy of following the path (°) ~-~ 识别按照路径走的起步角度精度(°)
Shelf laser noise deduction angle (deg) ~-~ 货架激光噪点的扣除角度(deg)
Laser positioning when rotating in place after recognition ~-~ 识别后原地旋转时采用激光定位
Forklift recognition shelf lateral deviation (m) ~-~ 叉车识别货架横向最大偏差(m)
Forklift recognition shelf angle maximum deviation (deg) ~-~ 叉车识别货架角度最大偏差(deg)
Recognize Bezier curve planning ~-~ 识别贝塞尔曲线规划
Identify the optimization times of Bezier curve planning ~-~ 识别贝塞尔曲线规划优化次数
Recognize Bezier curve forward distance (m) ~-~ 识别贝塞尔曲线前移距离(m)
Identify the maximum optimized curvature of Bezier curve ~-~ 识别贝塞尔曲线最大优化曲率
Identify the optimization times of straight-line planning ~-~ 识别直线规划优化次数
Recognize the maximum included angle of a straight line (°) ~-~ 识别直线最大夹角(°)
Does the free navigation support reversing ~-~ 自由导航是否支持倒车
Free navigation planning step ~-~ 自由导航规划步长
Free navigation smooth curve parameter ~-~ 自由导航光滑曲线参数
Free navigation smooth curve parameter ~-~ 自由导航光滑曲线参数
Free navigation smooth curve parameter ~-~ 自由导航光滑曲线参数
Free navigation smooth curve iteration times ~-~ 自由导航光滑曲线迭代次数
Free navigation of smooth curve obstacle distance range ~-~ 自由导航光滑曲线障碍物的距离范围
Free navigation local search path maximum time (ms) ~-~ 自由导航局部搜索路径最大时间(ms)
Free navigation local planning maximum time (ms) ~-~ 自由导航局部规划最多时间(ms)
Free navigation local planning lead distance (m) ~-~ 自由导航局部规划前置距离(m)
Free Navigation Whether Use Fit ~-~ 自由导航是否Use Fit
Whether to bypass in real time ~-~ 是否实时绕行
Maximum duration of failure of free navigation planning (s) ~-~ 自由导航规划失败持续最长时间(s)
Extra predicted distance of free navigation obstacles on ObsStopDist (m) ~-~ 自由导航障碍物在ObsStopDist上的额外预测距离(m)
Whether to prohibit lines with the same starting point and ending point ~-~ 是否禁止起点和终点一致的线路
The speed to identify the target point (m/s), only supports fork to pick the pallet ~-~ 去识别目标点的速度(m/s),只支持叉取栈板
Recognize the effective distance of the target speed (m), only support fork to pick the pallet ~-~ 识别目标点速度的起效距离(m),只支持叉取栈板
Do not check DO status before setting DO ~-~ 设置DO前不检查DO状态
In-situ rotation report error check of steering wheel ~-~ 舵轮车原地旋转报错检查
Type of calibration task ~-~ 标定任务的类型
Control period assumed in calibration (s) ~-~ 标定中假设的控制周期(s)
The reference angular velocity (deg/s) used for maximum velocity/acceleration calibration ~-~ 最大速度/加速度标定使用的参考角速度(deg/s)
Maximum speed/acceleration calibration time waiting for acceleration to start (s) ~-~ 最大速度/加速度标定中等待加速开始的时长(s)
The length of the mean filter in the maximum speed/acceleration calibration (s) ~-~ 最大速度/加速度标定中均值滤波器的长度(s)
The ratio of the final speed to the maximum speed in the maximum speed/acceleration calibration ~-~ 最大速度/加速度标定中终速度与最大速度的比率
The ratio of the lower bound of acceleration and deceleration in the maximum speed/acceleration calibration ~-~ 最大速度/加速度标定中判定加减速段下界的比率
The ratio of the upper bound of the acceleration/deceleration segment in the maximum speed/acceleration calibration ~-~ 最大速度/加速度标定中判定加减速段上界的比率
Determine the fluctuation ratio of the constant speed section in the maximum speed/acceleration calibration ~-~ 最大速度/加速度标定中判定匀速段的波动比率
Maximum speed/acceleration calibration constant speed segment duration (s) ~-~ 最大速度/加速度标定中匀速段的持续时长(s)
The length of time to wait for the robot to stop after calibration (s) ~-~ 标定结束后等待机器人停止的时长(s)
Maximum speed/acceleration insurance coefficient ~-~ 最大速度/加速度的保险系数
Angular acceleration of the wheel used for minimum speed calibration (deg/s^2) ~-~ 最小速度标定所使用的轮子角加速度(deg/s^2)
The length of the speed check window used for minimum speed calibration (s) ~-~ 最小速度标定所使用的速度检查窗口长度(s)
Interval duration of switching motion direction in minimum speed calibration (s) ~-~ 最小速度标定中切换运动方向的间隔时长(s)
Determine the effective speed response ratio of the minimum execution speed ~-~ 判定最小执行速度有效的速度响应比率
Safety factor for minimum executable speed ~-~ 最小可执行速度的保险系数
Minimum execution speed calibration for the minimum duration of acceleration phase (s) ~-~ 最小执行速度标定中加速阶段持续的最短时间(s)
Rotational angular velocity (deg/s) during IMU yaw angle coefficient calibration ~-~ IMU偏摆角系数标定时的旋转角速度(deg/s)
Rotational angular acceleration of IMU yaw angle coefficient calibration (deg/s^2 ) ~-~ IMU偏摆角系数标定时的旋转角加速度(deg/s^2)
ImU yaw angle coefficient calibration rotation angle deceleration (deg/s^ 2) ~-~ IMU偏摆角系数标定时的旋转角减速度(deg/s^2)
IMU yaw angle coefficient calibration rotation angle (deg) ~-~ IMU偏摆角系数标定旋转的角度(deg)
Acc./Dec. for IMU initial calibration(m/s^2) ~-~ Acc./Dec. for IMU initial calibration(m/s^2)
Angular Acc./Dec. for IMU initial calibration(deg/s^2)  ~-~ Angular Acc./Dec. for IMU initial calibration(deg/s^2)
Max vel. for IMU initial calibration(m/s) ~-~ Max vel. for IMU initial calibration(m/s)
Max angular vel. for IMU initial calibration(deg/s) ~-~ Max angular vel. for IMU initial calibration(deg/s)
The Q value of the differential car LQR, the larger the follow-up effect, the better the jitter ~-~ 差动车 LQR 的 Q 值，越大跟随效果越好，但是抖动也会增强
Magnetic stripe debug output ~-~ 磁条调试输出
Number read by the magnetic stripe sensor ~-~ 磁条传感器读到的个数
Acceleration is not considered for translational rotation ~-~ 平动转动不考虑加速度
Shelf leg reflectivity ~-~ 货架腿反射率
Robot adjustment distance (m) ~-~ 机器人调整距离(m)
Preset distance(m) ~-~ 预置距离(m)
Valid shelf leg spacing (m) ~-~ 有效货架腿间距(m)
Do not modify ~-~ 请勿修改
Inside distance of shelf leg(m) ~-~ 货架腿内侧距离(m)
Outside distance of shelf leg(m) ~-~ 货架腿外侧距离(m)
Depth into the shelf (m) ~-~ 潜入货架的深度(m)
Shelf Length(m) ~-~ 货架长度(m)
Barrier around: acceleration regularization weight ~-~ 绕障：加速度正则化权重
Barrier bypass: Delay parameter(s) ~-~ 绕障：延时参数(s)
Barrier bypass: thread break time parameter ( s) ~-~ 绕障：线程休息时间参数(s)
Barrier around: global path linear acceleration (m/s^2) ~-~ 绕障：全局路径线加速度(m/s^2)
Obstacle around: global path curvature acceleration (rad/s^2) ~-~ 绕障：全局路径曲率加速度(rad/s^2)
obstacle bypass: local tracking linear acceleration (m/s^2) ~-~ 绕障：局部跟踪线加速度(m/s^2)
Barrier around: local angular acceleration (rad/s^2) ~-~ 绕障：局部角加速度(rad/s^2)
Barrier: Linear acceleration near the end point (m/s^2) ~-~ 绕障：终点附近线加速度(m/s^2)
Obstacle around: angular acceleration near the end point (rad/s^2) ~-~ 绕障：终点附近角加速度(rad/s^2)
obstacle circumvention: acceleration to point (m/s^2) ~-~ 绕障：到点加速度(m/s^2)
Barrier around: Tracking weight ~-~ 绕障：跟踪权重
Obstacle bypass: to point tracking weight ~-~ 绕障：到点跟踪权重
Barrier around: time weight ~-~ 绕障：时间权重
Barrier around: Time weight at arrival ~-~ 绕障：到点时间权重
Barrier around: angular acceleration regularization weight ~-~ 绕障：角加速度正则化权重
Obstacle around: to point angular acceleration regularization weight ~-~ 绕障：到点角加速度正则化权重
Barrier around: Maximum linear speed (m/s) ~-~ 绕障：最大线速度(m/s)
obstacle circumvention: maximum angular velocity (rad/s) ~-~ 绕障：最大角速度(rad/s)
Barrier bypass: Log status ~-~ 绕障：Log 状态
Barrier bypass: global path clipping value ~-~ 绕障：全局路径裁剪值
Barrier around: Path clipping length (m) ~-~ 绕障：路径裁剪长度(m)
Obstacle bypass: control period (ms) ~-~ 绕障：控制周期(ms)
Obstacle: Global Path Jerk Value (m/s^2) ~-~ 绕障：全局路径 Jerk 值(m/s^2)
Obstacle bypass: the tolerance of the global path to obstacles (m), which is the safety distance Minus the distance between the obstacle and the robot ~-~ 绕障：全局路径对障碍物的容忍(m)，即安全距离减去障碍物离机器人的距离
The distance to the follower (meters) ~-~ 与被跟随者之间的距离(米)
The angle difference with the follower (degrees) ~-~ 与被跟随者之间的角度差(度)
Follow to open obstacle avoidance ~-~ 跟随开启避障
The vKp value of the two-wheel differential module car ~-~ 双轮差速模组车的 vKp 值
VKd value of two-wheel differential module car ~-~ 双轮差速模组车的 vKd 值
The wKp value of the two-wheel differential module car ~-~ 双轮差速模组车的 wKp 值
wKd value of two-wheel differential module car ~-~ 双轮差速模组车的 wKd 值
Steer Kp value of two-wheel differential module car module 1 ~-~ 双轮差速模组车模组1的steer Kp 值
steer Kd value of two-wheel differential module car module 1 ~-~ 双轮差速模组车模组1的steer Kd 值
steer Kp value of two-wheel differential module car module 2 ~-~ 双轮差速模组车模组2的steer Kp 值
Steer Kd value of two-wheel differential module car module 2 ~-~ 双轮差速模组车模组2的steer Kd 值
Module 1 minimum rudder angle resolution (degrees) ~-~ 模组1最小舵角分辨率(度)
Module 2 minimum rudder angle resolution (degrees) ~-~ 模组2最小舵角分辨率(度)
Do not use acceleration changes ~-~ 不采用加速度变化
Barrier around: acceleration regularization weight ~-~ 绕障：加速度正则化权重
Barrier bypass: Delay parameter(s) ~-~ 绕障：延时参数(s)
Barrier bypass: thread break time parameter ( s) ~-~ 绕障：线程休息时间参数(s)
Barrier: Global path linear acceleration (m/s^2) ~-~ 绕障：全局路径线加速度(m/s^2)
Obstacle around: global path curvature acceleration (rad/s^2) ~-~ 绕障：全局路径曲率加速度(rad/s^2)
obstacle bypass: local tracking linear acceleration (m/s^2) ~-~ 绕障：局部跟踪线加速度(m/s^2)
Barrier around: local angular acceleration (rad/s^2) ~-~ 绕障：局部角加速度(rad/s^2)
Barrier around: linear acceleration near the end point (m/s^2) ~-~ 绕障：终点附近线加速度(m/s^2)
Barrier around: angular acceleration near the end point (rad/s^2) ~-~ 绕障：终点附近角加速度(rad/s^2)
Barrier around: Acceleration to point (m/s^2) ~-~ 绕障：到点加速度(m/s^2)
Barrier around: Tracking weight ~-~ 绕障：跟踪权重
Obstacle bypass: to point tracking weight ~-~ 绕障：到点跟踪权重
Barrier around: time weight ~-~ 绕障：时间权重
Barrier around: Time weight at arrival ~-~ 绕障：到点时间权重
Barrier around: angular acceleration regularization weight ~-~ 绕障：角加速度正则化权重
Obstacle around: to point angular acceleration regularization weight ~-~ 绕障：到点角加速度正则化权重
Barrier around: Maximum linear speed (m/s) ~-~ 绕障：最大线速度(m/s)
Obstacle: Maximum angular velocity (rad/s) ~-~ 绕障：最大角速度(rad/s)
Barrier bypass: Log status ~-~ 绕障：Log 状态
Barrier bypass: global path clipping value ~-~ 绕障：全局路径裁剪值
Barrier around: Path cut length (m) ~-~ 绕障：路径裁剪长度(m)
Obstacle bypass: control period (ms) ~-~ 绕障：控制周期(ms)
Barrier bypass: global path Jerk value (m/s^2) ~-~ 绕障：全局路径 Jerk 值(m/s^2)
Barrier around: the tolerance of the global path to obstacles (m), which is the safe distance Minus the distance between the obstacle and the robot ~-~ 绕障：全局路径对障碍物的容忍(m)，即安全距离减去障碍物离机器人的距离
Debug output ~-~ 调试输出
Do not use acceleration changes ~-~ 不采用加速度变化
The x value of the omnidirectional car LQR, the larger the follow-up effect, the better the jitter ~-~ 全向车 LQR 的 x 值，越大跟随效果越好，但是抖动也会增强
VKp value of omnidirectional vehicle PID ~-~ 全向车 PID 的 vKp 值
VKd value of omnidirectional vehicle PID ~-~ 全向车 PID 的 vKd 值
WKp value of omnidirectional vehicle PID ~-~ 全向车 PID 的 wKp 值
wKd value of omnidirectional vehicle PID ~-~ 全向车 PID 的 wKd 值
Barrier around: acceleration regularization weight ~-~ 绕障：加速度正则化权重
Barrier bypass: Delay parameter(s) ~-~ 绕障：延时参数(s)
Barrier bypass: thread break time parameter ( s) ~-~ 绕障：线程休息时间参数(s)
Barrier: Global path linear acceleration (m/s^2) ~-~ 绕障：全局路径线加速度(m/s^2)
Obstacle around: global path curvature acceleration (rad/s^2) ~-~ 绕障：全局路径曲率加速度(rad/s^2)
obstacle bypass: local tracking linear acceleration (m/s^2) ~-~ 绕障：局部跟踪线加速度(m/s^2)
Barrier around: local angular acceleration (rad/s^2) ~-~ 绕障：局部角加速度(rad/s^2)
Barrier around: Linear acceleration near the end point (m/s^2) ~-~ 绕障：终点附近线加速度(m/s^2)
Obstacle around: angular acceleration near the end point (rad/s^2) ~-~ 绕障：终点附近角加速度(rad/s^2)
Barrier around: Acceleration to point (m/s^2) ~-~ 绕障：到点加速度(m/s^2)
Barrier around: tracking weight ~-~ 绕障：跟踪权重
Obstacle bypass: to point tracking weight ~-~ 绕障：到点跟踪权重
Barrier around: time weight ~-~ 绕障：时间权重
Barrier around: Time weight at arrival ~-~ 绕障：到点时间权重
Barrier around: angular acceleration regularization weight ~-~ 绕障：角加速度正则化权重
Obstacle around: to point angular acceleration regularization weight ~-~ 绕障：到点角加速度正则化权重
Barrier around: Maximum linear speed (m/s) ~-~ 绕障：最大线速度(m/s)
Obstacle: Maximum angular velocity (rad/s) ~-~ 绕障：最大角速度(rad/s)
Barrier bypass: Log status ~-~ 绕障：Log 状态
Barrier bypass: global path clipping value ~-~ 绕障：全局路径裁剪值
Barrier around: Path cut length (m) ~-~ 绕障：路径裁剪长度(m)
Obstacle bypass: control period (ms) ~-~ 绕障：控制周期(ms)
Way around: global path Jerk value (m/s^2) ~-~ 绕障：全局路径 Jerk 值(m/s^2)
Obstacle: The tolerance of the global path to obstacles (m), which is the safe distance Minus the distance between the obstacle and the robot ~-~ 绕障：全局路径对障碍物的容忍(m)，即安全距离减去障碍物离机器人的距离
Do not use acceleration changes ~-~ 不采用加速度变化
Shelf Length(m) ~-~ 货架长度(m)
Shelf leg reflectivity ~-~ 货架腿反射率
Shelf angle range (°) ~-~ 货架角度范围(°)
Do not modify ~-~ 请勿修改
Do not modify ~-~ 请勿修改
Do not modify ~-~ 请勿修改
Do not modify ~-~ 请勿修改
Do not modify ~-~ 请勿修改
Inside distance of shelf leg(m) ~-~ 货架腿内侧距离(m)
Outside distance of shelf leg (m) ~-~ 货架腿外侧距离(m)
Do not modify ~-~ 请勿修改
Drill Shelf Laser Debug Switch ~-~ 钻货架激光调试开关
Do not modify ~-~ 请勿修改
Do not modify ~-~ 请勿修改
Do not modify ~-~ 请勿修改
Do not modify ~-~ 请勿修改
The x value of the omnidirectional car LQR, the larger the following effect, the better, but the jitter will also increase ~-~ 全向车 LQR 的 x 值，越大跟随效果越好，但是抖动也会增强
The y value of the omnidirectional car LQR, the larger the follow-up effect, the better the jitter ~-~ 全向车 LQR 的 y 值，越大跟随效果越好，但是抖动也会增强
The theta value of the LQR of an omnidirectional car, the larger the follow-up effect, the better the jitter ~-~ 全向车 LQR 的 theta 值，越大跟随效果越好，但是抖动也会增强
Type of calibration task ~-~ 标定任务的类型
Control period assumed in calibration (s) ~-~ 标定中假设的控制周期(s)
Maximum speed/acceleration reference angular velocity (deg/s) ~-~ 最大速度/加速度标定使用的参考角速度(deg/s)
Maximum speed/acceleration calibration waiting time for acceleration to start (s) ~-~ 最大速度/加速度标定中等待加速开始的时长(s)
The length of the mean filter in the maximum speed/acceleration calibration (s) ~-~ 最大速度/加速度标定中均值滤波器的长度(s)
The ratio of the final speed to the maximum speed in the maximum speed/acceleration calibration ~-~ 最大速度/加速度标定中终速度与最大速度的比率
The ratio of the lower bound of acceleration and deceleration in the maximum speed/acceleration calibration ~-~ 最大速度/加速度标定中判定加减速段下界的比率
The ratio of the upper bound of the acceleration/deceleration segment in the maximum speed/acceleration calibration ~-~ 最大速度/加速度标定中判定加减速段上界的比率
Determine the fluctuation ratio of the constant speed segment in the maximum speed/acceleration calibration ~-~ 最大速度/加速度标定中判定匀速段的波动比率
Maximum speed/acceleration calibration constant speed segment duration (s) ~-~ 最大速度/加速度标定中匀速段的持续时长(s)
The length of time to wait for the robot to stop after the calibration (s) ~-~ 标定结束后等待机器人停止的时长(s)
Maximum Speed/Acceleration Insurance Coefficient ~-~ 最大速度/加速度的保险系数
Angular acceleration of the wheel used for minimum speed calibration (deg/s^2) ~-~ 最小速度标定所使用的轮子角加速度(deg/s^2)
The length of the speed check window used for minimum speed calibration (s) ~-~ 最小速度标定所使用的速度检查窗口长度(s)
Interval duration for switching the direction of motion in the minimum speed calibration (s) ~-~ 最小速度标定中切换运动方向的间隔时长(s)
Determine the effective speed response ratio of the minimum execution speed ~-~ 判定最小执行速度有效的速度响应比率
Safety factor for minimum executable speed ~-~ 最小可执行速度的保险系数
Minimum duration of acceleration phase in minimum execution speed calibration (s) ~-~ 最小执行速度标定中加速阶段持续的最短时间(s)
Rotational angular velocity during IMU yaw angle coefficient calibration (deg/s) ~-~ IMU偏摆角系数标定时的旋转角速度(deg/s)
The rotational angular acceleration of the IMU yaw angle coefficient calibration (deg/s^2 ) ~-~ IMU偏摆角系数标定时的旋转角加速度(deg/s^2)
ImU yaw angle coefficient calibration rotation angle deceleration (deg/s^ 2) ~-~ IMU偏摆角系数标定时的旋转角减速度(deg/s^2)
IMU yaw angle coefficient calibration rotation angle (deg) ~-~ IMU偏摆角系数标定旋转的角度(deg)
Response time calibration front wheel rotation determination threshold (deg/s) ~-~ 响应时间标定前轮旋转判定阈值(deg/s)
Response time calibration front wheel linear speed reference value (m/s) ~-~ 响应时间标定前轮线速度参考值(m/s)
The reference acceleration and deceleration speed of the front wheel in the speed step test (m/s^ 2) ~-~ 速度阶跃测试中前轮的参考加减速度(m/s^2)
Waiting time for constant speed section and stop in speed step test (s) ~-~ 速度阶跃测试中匀速段和停止的等待时长(s)
Speed ​​step test front wheel reference speed (m/s) ~-~ 速度阶跃测试前轮的参考速度(m/s)
Reference rudder angle for rudder angle step test (deg) ~-~ 舵角阶跃测试的参考舵角(deg)
Wait for the steering wheel to return to zero in the dead zone calibration (s) ~-~ 舵轮死区标定中等待舵轮归零的时长(s)
The speed of the steering wheel reference angle increase in the dead zone calibration (deg/s) ~-~ 舵轮死区标定中舵轮参考角度增长的速度(deg/s)
Rudder angle movement determination threshold (deg) ~-~ 舵轮死区标定中舵角移动判定阈值(deg)
Safety coefficient of steering wheel dead zone ~-~ 舵轮死区的保险系数
The initial stage of the minimum speed calibration avoids the wheel reference angular speed issued by the start delay ( deg/s) ~-~ 最小速度标定起始阶段避免起动延时下发的轮子参考角速度(deg/s)
In the initial stage of minimum speed calibration, avoid the execution of starting delay and issuing small reference speed Time(s) ~-~ 最小速度标定起始阶段避免起动延时下发小参考速度的执行时间(s)
Debug output ~-~ 调试输出
Debug output ~-~ 调试输出
Back distance after identification point (m) ~-~ 识别点后的后退距离(m)
Front distance before identification point (m) ~-~ 识别点前的前置距离(m)
Override recognition height, less than 0 do not enable (m) ~-~ 覆盖识别高度，小于 0 不启用(m)
After the forklift picks up the goods, the additional lift height of the fork (m) ~-~ 叉车取货物后，货叉额外抬升的高度(m)
Forklift recognition, the height of the fork (m) ~-~ 叉车识别时，货叉的高度(m)
DHL forklift automatic restart waiting time ~-~ DHL叉车自动重启等待时间
The Q value of the steering wheel vehicle LQR, the larger the following effect, the better, but the jitter will also increase ~-~ 舵轮车 LQR 的 Q 值，越大跟随效果越好，但是抖动也会增强
RBKSim sleep time(unit: ms) ~-~ RBKSim sleep time(单位:ms)
laser dist (unit: m) ~-~ laser dist (单位:m)
RBKSimrobot dt (unit: s) ~-~ RBKSimrobot dt (单位:s)
Sim Battery Percentage (Unit:%) ~-~ Sim Battery Percentage (单位:%)
is charing ~-~ is charing
auto charing ~-~ auto charing
auto charing (unit: m) ~-~ auto charing (单位:m)
steer step (unit: deg) ~-~ steer step (单位:deg)
print log ~-~ print log
auto update map ~-~ auto update map
Sensor Fusion Data Debugging Switch ~-~ 传感器融合数据调试开关
sensor fusion data debugging type. 0: local; 1: global; 2: all ~-~ 传感器融合数据调试种类. 0: 局部； 1: 全局; 2: 所有
Sensor point cloud retention point distance ~-~ 传感器点云保留点距离
Laser Point Retention Time(s) ~-~ 激光点保留时间(s)
The angular interval of virtual laser points (°) ~-~ 虚拟激光点的角度间隔(°)
Cutting out area debugging switch ~-~ 抠出区域调试开关
The number of laser points after resampling ~-~ 对激光点数进行重采样后的点数
Camera point cloud filter number ~-~ 摄像头点云滤波数目
Camera point cloud resolution (m) ~-~ 摄像头点云分辨率(m)
3D Laser point cloud resolution(m) ~-~ 3D Laser点云分辨率(m)
3D Laser MinHeight(m) ~-~ 3D Laser最低高度(m)
Depth camera maximum X range (m) ~-~ 深度摄像头最大X范围(m)
Depth camera maximum Y range (m) ~-~ 深度摄像头最大Y范围(m)
Map point maximum radius (m) ~-~ 地图点最大半径(m)

Port of general purpose graphic UDP server (restart to become effective) ~-~ 通用图形UDP 服务器端口（重启有效）
Maximum connections of general purpose graphic UDP server ~-~ 通用图形UDP 服务器允许的最大连接数
Push data interval of general purpose graphic UDP server (ms) ~-~ 通用图形UDP 服务器推送数据间隔（ms）
Maximum connections of status API ~-~ status API允许的最大连接数
Maximum connections of control API ~-~ control API允许的最大连接数
Maximum connections of task API ~-~ task API允许的最大连接数
Maximum connections of config API ~-~ config API允许的最大连接数
Maximum connections of other API ~-~ other API允许的最大连接数
Maximum connections of push API ~-~ push API允许的最大连接数
Default to automatic mode ~-~ 启动后默认为自动模式
Robot Home 1 ~-~ Robot Home 1
Robot Home 2 ~-~ Robot Home 2
Robot Home 3 ~-~ Robot Home 3
Robot Home 4 ~-~ Robot Home 4
Robot Home 5 ~-~ Robot Home 5
Startup taskchain ~-~ 启动后默认运行的任务链
IP address of dispatch system ~-~ 调度服务器 IP 地址
Port of dispatch system (default: 6379=redis, 15400=tcp) ~-~ 调度服务器端口号(default: 6379=redis, 15400=tcp)
Port of SRD ~-~ SRD 端口
Protocol version of dispatch system, change the IP and port simultaneously (restart to become effective) (1=redis_v1, 2=redis_v2, 3=tcp) ~-~ 调度协议版本, 注意相应修改IP和端口号(需永久修改，重启后生效) (1=redis_v1, 2=redis_v2, 3=tcp)
Alarm after disconnecting from the dispatch system ~-~ 与调度服务器断开后是否报警
Interval of disconnection detection with dispatch system (s) ~-~ 与调度服务器通信断连检测时间间隔(s)
Interval of push API data (ms) ~-~ 更新 PushData 的时间间隔(ms)
Port of ModBus TCP ~-~ ModBus TCP 端口号
Debug mode of ModBus ~-~ ModBus 调试模式
Robot name ~-~ 机器人名称,即调度系统中机器人的 ID
Robot note, used to note the robot, easy to remember ~-~ 机器人备注,用于备注机器人,方便操作人员记忆
IP address of arm ~-~ 机械臂 IP 地址
It is forbidden to confirm localization when the confidence is lower than this value ~-~ 置信度低于该值时, 禁止确认定位正确
Maximum speed when controlled by controller (m/s) ~-~ 手柄控制时的最大速度(m/s)
Maximum speed of fork when controlled by controller (m/s) ~-~ 手柄控制时叉车的最大速度(m/s)
Maximum rotation speed when controlled by controller (°/s) ~-~ 手柄控制时的最大转速度(°/s)
Init point when controlled by controller ~-~ 手柄控制起始点
Whether to perform laser sampling in TCP API (the sampling resolution is 0.5°) ~-~ TCP API 中是否进行激光采样(采样强制分辨率为 0.5°)
Wireless network card name (eth1: Wifi client, wlp1s0/wlan0: build-in wireless network card);If you fill in the IP address, this IP address will be displayed ~-~ 无线网络使用的网卡(eth1:　无线客户端，　wlp1s0/wlan0:　内置无线网卡)；如果填写 IP 地址，则直接用此 IP 地址状态显示
Mac network card name (restart to become effective) ~-~ Mac网卡名称(需永久修改，重启后生效)
The duration of open-loop motion instruction issuing speed (ms) ~-~ 开环运动指令下发速度的持续时间(ms)
Information publish interval (s) ~-~ 信息发布时间间隔(s)
19301 data publish interval (ms) ~-~ 19301 信息发布时间间隔(ms)
The interval for reporting status data to dispatch system (ms) ~-~ 上报调度 status 信息的时间间隔(ms)
dispatch task status cycle (ms) ~-~ 调度任务状态循环周期(ms)
IP address of vision server ~-~ 视觉服务器 IP 地址
HTTP port of vision server ~-~ 视觉服务器 Http 端口号
In steer mode, the steer angle increment value (°) ~-~ 舵角控制模式下，舵角递增值(°)
When the signal value of the currently connected AP is lower than WifiSignalLevelKeep, the number of wireless scans exceeds this value before active roaming ~-~ 当前所连接 AP 信号值低于 WifiSignalLevelKeep 时，无线扫描次数超过该值后，再主动漫游
The quantity of APs scanned ~-~ 扫描 AP 数量
When the signal value is lower than this value, try to connect to an AP with a signal value higher than (current signal + WifiSignalLevelDiff) ~-~ 低于该信号强度值，尝试连接信号值高于 (current signal + WifiSignalLevelDiff) 的 AP
When the signal of the currently connected AP is lower than WifiSignalLevelKeep, try to connect to an AP whose signal is higher than (current signal + WifiSignalLevelDiff) ~-~ 当前所连接 AP 信号值低于 WifiSignalLevelKeep 时，尝试连接信号值高于(current signal + WifiSignalLevelDiff)的 AP

Peripheral ModbusTCP IP address ~-~ 外设 ModbusTCP IP 地址
Peripheral ModbusTCP port ~-~ 外设 ModbusTCP 端口
Peripheral ModbusTCP allows the use of read-only address bits ~-~ 外设 ModbusTCP 允许使用只读地址位
Peripheral ModbusTCP connection problem times>This parameter will report an error ~-~ 外设 ModbusTCP 连接有问题次数>该参数才进行报错
It is allowed to fail the parameter times in the Action before the error is reported ~-~ Action中允许失败该参数次才进行报错

Filtering parameters~-~滤波参数
COM port number~-~COM 端口号
Baud rate~-~波特率
Serial port to network port~-~串口转网口
Display maximum RSSI~-~显示最大RSSI
Timestamp server address~-~时间戳服务器地址
Time synchronization period (s)~-~时间同步周期(s)
Velodyne frequency~-~Velodyne 频率
Velodyne resolution~-~Velodyne 分辨率
Velodyne Laser Line ID~-~Velodyne 激光线 ID
Laser data recording time interval (s)~-~激光数据记录时间间隔(s)
Filter type, 0 = none,1 = average,2 = median,3 = maximum,4 = remission~-~滤波类型, 0 = 无,1 = 平均,2 = 中位数,3 = 最大,4 = 强度
Filter width, 0= two, 1= four, 2 = eight~-~滤波宽度, 0= 2, 1= 4, 2 = 8
Set filter~-~设置滤波
Number of laser points per frame~-~每帧激光点数量
Laser release frame rate~-~激光发布帧率
Rssi threshold for filtering low reflection points~-~过滤低反射点Rssi阈值
Obstacle height~-~障碍物高度
sleep time~-~睡眠时间
Rssi threshold for filtering low reflection points~-~过滤低反射点Rssi阈值
max range of laser~-~激光最大扫描距离

laser type ~-~ 激光设备类型
laser device ~-~ 激光设备
basic parameter ~-~ 基础参数
angle resolution ~-~ 角度分辨率
start angle ~-~ 起始角度
end angle ~-~ 终止角度
is upside ~-~ 是否正装
use for localization ~-~ 用于定位
use for 3D localization ~-~ 用于3D定位
use GPS for time synchronization ~-~ 使用GPS时间同步
camera type ~-~ 相机设备类型
camera device ~-~ 相机设备
only use for pallet detection ~-~ 仅用于识别栈板
camera brand ~-~ 相机品牌
is 3D camera ~-~ 是3D相机

obstacle height whcih can be detected ~-~ 障碍物最小高度
hole depth ~-~ 坑洞深度
threshold of yaw angle ~-~ yaw角度偏差阈值
max height which can be detected ~-~ 高空物体最大高度
grid size for filtering ~-~ 滤波格网大小
use calibration ~-~ 是否进行标定
camera horitontal view ~-~ 相机水平视角
camera vertical view ~-~ 相机垂直视角
max distance which can be detected by camera ~-~ 相机检测最远距离
tag size ~-~ 二维码尺寸
tag center height from ground ~-~ 二维码中心离地高度
The distance between AGV center and tag center ~-~ 二维码距离里程中心距离
The distance between two tag center ~-~两个二维码中心水平距离
start calib camera ~-~ 开始标定相机
record camera pointcloud ~-~ 记录点云数据
angle threshold between AGV and pallet ~-~ 被识别物体和机器人角度偏差阈值
truncated height used for pallet detection ~-~ 栈板识别截断高度
distance threshold between AGV and pallet in y direction ~-~ 栈板水平相对叉车偏差阈值
fork length to AGV center ~-~ 叉齿到里程中心距离
pallet detection score threshold ~-~ 栈板识别得分阈值
The number of detection used for tag detection ~-~ 识别拍摄次数
The max distance betweend pallet and AGV in X direction ~-~ 栈板离相机最远距离
use line noise filter ~-~ 是否使用线状噪声滤波
line noise filter range ~-~ 线状噪声滤波范围
point number threshold for line noise filter ~-~ 判断线状噪声个数阈值
angle threshold for line noise filter ~-~ 线状滤波角度阈值
distance threshold for line noise filter ~-~ 线状滤波距离阈值
The actual value is the set value K/1000 ~-~ 实际值为设定值K/1000
chassis device type ~-~ 底盘设备类型
chassis ~-~ 底盘
basic parameters ~-~ 基础参数
sports mode ~-~ 运动模式
rear wheel drive ~-~ 后轮驱动
The change of the wheelbase of the forklift when loading goods ~-~ 叉车在加载货物的时候轴距的变化
roller angle ~-~ 轮辊角
revolver of differential module 1 ~-~ 差动模组1的左轮
right wheel of differential module 1 ~-~ 差动模组1的右轮
passive steering wheel of differential module 1 ~-~ 差动模组1的被动舵轮
revolver of differential module 2 ~-~ 差动模组2的左轮
right wheel of differential module 2 ~-~ 差动模组2的右轮
passive steering wheel of differential module 2 ~-~ 差动模组2的被动舵轮
Robot chassis shape ~-~ 机器人底盘形状
rectangle ~-~ 矩形
wide ~-~ 宽
head ~-~ 头
tail ~-~ 尾
robot height ~-~ 机器人高度
circle ~-~ 圆形
radius ~-~ 半径
robot height ~-~ 机器人高度
charger ~-~ 充电机构
charger ~-~ 充电机构
basic parameters ~-~ 基础参数
The x of the charging pile in the center coordinate system of the vehicle body ~-~ 充电桩在车体中心坐标系下的x
The y of the charging pile in the center coordinate system of the vehicle body ~-~ 充电桩在车体中心坐标系下的y
The angle of the charging pile in the center coordinate system of the vehicle body ~-~ 充电桩在车体中心坐标系下的角度
id number of charging DO, -1 means that this DO does not exist ~-~ 充电DO的id号,-1表示不存在这个DO
Number of attempts to open and close the charging DO ~-~ 充电DO打开关闭的尝试次数
Charging DO is opening and closing, the duration of keeping it open ~-~ 充电DO打开关闭中,保持打开的持续时间
fix the path to charge, if the distance is less than this distance, open the charging DO ~-~ 固定路径去充电，小于此距离，将充电DO打开
the id number of the charging trigger DI, -1 means there is no such DI ~-~ 充电触发DI的id号,-1表示不存在这个DI
The id number of the DI triggered when the charging position is reached, and the charging DO is turned on, -1 means there is no such DI ~-~ 到达充电位置触发DI的id号,并打开充电DO，-1表示不存在这个DI
Maximum time for automatic charging, timing when the task starts ~-~ 自动充电执行最长时间，任务开始时计时
Maximum time for the charger to power on, and start timing when it reaches the charging position ~-~ 充电器上电最长时间,到达充电位置开始计时
charge running speed ~-~ 充电运行速度
Automatic charging lead distance ~-~ 自动充电前置距离
Automatic charging plan forward distance ~-~ 自动充电规划前移距离
Automatic charging adopts Bezier curve planning route ~-~ 自动充电采用Bezier曲线规划线路
Automatic charging Bezier curve front distance ~-~ 自动充电Bezier曲线前置距离
Automatic charging Bezier curve planning forward distance ~-~ 自动充电Bezier曲线规划前移距离
Whether to turn off charging DO during emergency stop ~-~ 拍急停时是否关闭充电DO
Use mileage mode when charging ~-~ 充电时使用里程模式
Whether to use the direction of the charging point on the map to cover the direction of the recognition result ~-~ 是否使用地图上充电点的方向覆盖识别结果的方向
Charge Motor Disable Time ~-~ 充电电机去使能时间
charging shielding laser ~-~ 充电屏蔽激光
type ~-~ 类型
goods detection ~-~ 货物检测
ignore task instruction ~-~ 忽略任务指令
basic parameters ~-~ 基础参数
script name ~-~ 脚本名称
Script parameters ~-~ 脚本参数
laser protection area ~-~ 激光保护区域
laser protection area ~-~ 激光保护区域
basic parameters ~-~ 基础参数
width ~-~ 宽度
Additional robot collision area ~-~ 机器人额外的碰撞区域
Additional robot collision area ~-~ 机器人额外的碰撞区域
basic parameters ~-~ 基础参数
Laser DeductArea ~-~ 激光扣除区域
Laser DeductArea ~-~ 激光扣除区域
basic parameters ~-~ 基础参数
Laser deduction area x minimum value ~-~ 激光扣除区域x最小值
laser deduction area y minimum value ~-~ 激光扣除区域y最小值
Laser deduction area x maximum value ~-~ 激光扣除区域x最大值
laser deduction area y maximum value ~-~ 激光扣除区域y最大值
laser deduction area z minimum value ~-~ 激光扣除区域z最小值
laser deduction area z maximum value ~-~ 激光扣除区域z最大值
The laser deduction area ignores the z axis ~-~ 激光扣除区域忽略z轴
basic parameters ~-~ 基础参数
pgv boot time ~-~ pgv开机时间
function ~-~ 功能
adjust ~-~ 调整
adjustment and positioning ~-~ 调整和定位
adjustment and positioning ~-~ 调整和定位
magnetic stripe sensor ~-~ 磁条传感器
magnetic stripe sensor ~-~ 磁条传感器
basic parameters ~-~ 基础参数
number of sensing points ~-~ 感应点个数
resolution ~-~ 分辨率
fork ~-~ 货叉
fork ~-~ 货叉
basic parameters ~-~ 基础参数
Forklift pickup in place switch ~-~ 叉车取货到位开关
Forklift pickup in place switch position x ~-~ 叉车取货到位开关位置x
Forklift cargo detection switch ~-~ 叉车货物检测开关
Goods detection anti-shake time ~-~ 货物检测防抖动时间
loading cargo delay time ~-~ 加载货物延时时间
Remove cargo delay time ~-~ 去除货物延时时间
DO controlled before raising the fork ~-~ 抬升货叉前控制的DO
DO status before raising the fork ~-~ 抬升货叉前DO的状态
DO controlled before dropping fork ~-~ 下降货叉前控制的DO
DO status before falling fork ~-~ 下降货叉前DO的状态
Fork shelf area ~-~ 货叉架子区域
Forklift deduction area effective fork height ~-~ 叉车扣除区域起效的货叉高度
the width of the shelf deduction area in the forklift coordinate system ~-~ 叉车坐标系下架子扣除区域的宽度
Xmax of the shelf deduction area under the forklift coordinate system ~-~ 叉车坐标系下架子扣除区域的Xmax
Xmin of the shelf deduction area under the forklift coordinate system ~-~ 叉车坐标系下架子扣除区域的Xmin
Forklift fork tip sensor ~-~ 叉车货叉尖端传感器
Di's id ~-~ Di的id
-1 is not enabled, >0 is filter time ~-~ -1为不启用, >0为滤波时间
Enable the fork tip sensor when loading goods ~-~ 装载货物时启用叉尖传感器
Enable fork tip sensor when unloading cargo ~-~ 卸载货物时启用叉尖传感器
Whether the error report of goods at the end point is automatically cleared ~-~ 终点有货物的报错是否自动清除
There is an error with goods at the end, the task failed ~-~ 终点有货物的报错,任务失败
Back Laser ~-~ 后置激光
Di laser id ~-~ Di激光的id
laser id ~-~ 激光的id
effective fork height ~-~ 起效的货叉高度
weighing function ~-~ 称重功能
Maximum weight, less than 0, this function is not enabled ~-~ 最大重量,小于0此功能不启用
filter time ~-~ 滤波时间
Control Method of Fork Mechanism ~-~ 货叉机构的控制方式
none ~-~ 无
Control up and down through DO, give priority to responding to DI ~-~ 通过DO控制升降，优先响应DI
Pump Motor DO ~-~ 泵电机DO
Release Valve DO ~-~ 泄流阀DO
upgrade DI ~-~ 抬升位DI
DI dropped into place ~-~ 下降到位DI
rise delay time ~-~ 上升延时时间
down delay time ~-~ 下降延时时间
By motor control ~-~ 通过电机控制
Open the height of safe driving speed limit ~-~ 开启安全行驶速度限制的高度
Safe Driving Speed ~-~ 安全行驶速度
If it is not empty, it means using the corresponding motor to control the fork lift ~-~ 如果非空，则表示用相应电机控制货叉抬升
Maximum fork lift speed when there is goods ~-~ 有货物时货叉抬升最大速度
Maximum speed of fork drop when there is goods ~-~ 有货物时货叉下降最大速度
traction ~-~ 牵引
traction ~-~ 牵引
Basic Settings ~-~ 基础设置
none ~-~ 无
Control action through DO ~-~ 通过DO控制动作
clamp DO ~-~ 抓取机DO
release DO ~-~ 释放DO
clamping completed DI ~-~ 抓取完成DI
Next release complete DI ~-~ 下释放完成DI
clamping delay time ~-~ 抓取延时时间
release delay time ~-~ 释放延时时间
audio player ~-~ 音频播放
audio player ~-~ 音频播放
basic parameters ~-~ 基础参数
File name of audio during navigation ~-~ 导航时音频的文件名
audio duration before navigation ~-~ 导航前的音频时长
Whether the audio is played in a loop during navigation ~-~ 导航时音频是否循环播放
file name of the audio when going backward ~-~ 倒走时音频的文件名
File name of the audio when turning left ~-~ 左转时音频的文件名
File name of audio when turning right ~-~ 右转时音频的文件名
audio file name when blocking ~-~ 阻挡时音频的文件名
audio file name when battery is low ~-~ 低电量时音频的文件名
the name of the audio file when the error is reported ~-~ 报错时音频的文件名
the file name of the audio when the collision occurs ~-~ 发生碰撞时音频的文件名
whether to play music ~-~ 是否播放音乐
Whether to play error audio based on error code ~-~ 是否依据错误码播放错误音频
Control method of jacking mechanism ~-~ 顶升机构的控制方式
Control method of jacking mechanism ~-~ 顶升机构的控制方式
basic parameters ~-~ 基础参数
counterpoint DI, -1 is not enabled ~-~ 对位DI,-1为不启用
counterpoint DI continuous detection time, after this time is continuously triggered, it is considered successful ~-~ 对位DI连续检测时间，连续触发该时间后认为成功
loading cargo delay time ~-~ 加载货物延时时间
Remove cargo delay time ~-~ 去除货物延时时间
Basic Settings ~-~ 基础设置
none ~-~ 无
Control jacking through DO ~-~ 通过DO控制顶升
top DI ~-~ 顶部DI
bottom DI ~-~ 底部DI
up DO ~-~ 上升DO
down DO ~-~ 下降DO
Max Speed ~-~ 最大速度
Max Height ~-~ 最大高度
rise delay time ~-~ 上升延时时间
down delay time ~-~ 下降延时时间
Lifting by motor control ~-~ 通过电机控制顶升
If it is not empty, it means that the corresponding motor is used to control the jacking ~-~ 如果非空，则表示用相应电机控制顶升
Cargo Inspection DI ~-~ 货物检测 DI
Communication and control the lifting mechanism through Seer Modbus protocol ~-~ 通过 Seer Modbus 协议进行通讯控制顶升机构
Whether to use as a traction mechanism ~-~ 是否当成牵引机构来使用
Collaboratively control follow-up and jacking through two motors ~-~ 通过两个电机协同控制随动和顶升
the name of the follower motor ~-~ 随动电机的名称
name of jacking linear motor ~-~ 顶升线性电机的名称
Height change coefficient corresponding to the angular velocity of the follower motor ~-~ 随动电机角速度对应的高度变化系数
filter coefficient ~-~ 滤波系数
Users control the lifting mechanism by themselves ~-~ 用户自行控制顶升机构
DO controlled motor ~-~ DO控制的电机
DO controlled motor ~-~ DO控制的电机
basic parameters ~-~ 基础参数
upper limit DI ~-~ 上限位DI
lower limit DI ~-~ 下限位DI
zero DI ~-~ 零位DI
action completion time, if there is no upper position switch, the action will be completed even after upDelayTime has passed ~-~ 动作完成时间，如果没有上到位开关，则过了upDelayTime就算动作完成
action completion time, if there is no bottom switch, the action will be completed even if downDelayTime has passed ~-~ 动作完成时间，如果没有下到位开关，则过了downDelayTime就算动作完 成
Passive Motor Name ~-~ 被动电机名字
motor DI ~-~ 电机DI
none ~-~ 无
up to place ~-~ 上升到位
ID corresponding to DI ~-~ 对应DI的id
down in place ~-~ 下降到位
ID corresponding to DI ~-~ 对应DI的id
basic parameters ~-~ 基础参数
drive CAN ID ~-~ 驱动器CAN的ID
Maximum drive speed ~-~ 驱动器最大转速
Is the drive reversed ~-~ 驱动器是否反向
encoder line number ~-~ 编码器线数
Upper limit DI (0-8 before H1.2.10, 0-10 after H1.2.10) ~-~ 上限位DI(H1.2.10以前为0-8, H1.2.10以后为0-10)
Lower limit DI (0-8 before H1.2.10, 0-10 after H1.2.10) ~-~ 下限位DI(H1.2.10以前为0-8, H1.2.10以后为0-10)
Zero DI (0-8 before H1.2.10, 0-10 after H1.2.10) ~-~ 零位DI(H1.2.10以前为0-8, H1.2.10以后为0-10)
Whether it is a passive motor (only feedback encoder information) ~-~ 是否为被动电机(仅反馈编码器信息)
whether you have a brake ~-~ 是否拥有抱闸
Port Settings ~-~ 端口设置
port1 ~-~ 端口1
port 2 ~-~ 端口2
Function Settings ~-~ 功能设置
walking motor ~-~ 行走电机
wheel radius ~-~ 轮子半径
reduction ratio ~-~ 减速比
minimum starting speed ~-~ 最小启动速度
Rotating Motor ~-~ 旋转电机
Max Speed ~-~ 最大速度
Max acceleration ~-~ 最大加速度
Maximum Deceleration ~-~ 最大减速度
maximum jerk ~-~ 最大加加速度
gear ratio multiplied by reducer reduction ratio ~-~ 齿轮比乘以减速机减速比
pallet rotation homing speed ~-~ 托盘旋转标零速度
paranoid angle ~-~ 偏执角度
-1 means not enabled, configure the DI, trigger during the zeroing process to report an error and stop, and continue to zero after contact (H1.2.10 is 0-8 before H1.2.10, 0-10 after H1.2.10) ~-~ -1表示不启用,配置该DI,在标零过程中触发即可报错停止,接触后继续标零(H1.2.10以前为0-8, H1.2.10以后为0-10)
steering wheel motor ~-~ 舵轮电机
Max Speed ~-~ 最大速度
max acceleration ~-~ 最大加速度
Max deceleration ~-~ 最大减速度
maximum jerk ~-~ 最大加加速度
steering wheel reduction ratio ~-~ 舵轮减速比
maximum rudder angle value ~-~ 最大舵角值
minimum rudder angle value ~-~ 最小舵角值
rudder angle offset ~-~ 舵角偏置
rudder angle resolution ~-~ 舵角分辨率
linear motor ~-~ 线性电机
linear motor reduction ratio ~-~ 线性电机减速比
linear motor zero speed ~-~ 线性电机标零速度
maximum length ~-~ 最大长度
minimum length ~-~ 最小长度
zero offset ~-~ 零位偏移量
up-to-place precision ~-~ 上到位精度
lower accuracy ~-~ 下到位精度
Max Speed ~-~ 最大速度
Max acceleration ~-~ 最大加速度
Maximum Deceleration ~-~ 最大减速度
maximum jerk ~-~ 最大加加速度
minimum ascending speed, 0 means not enabling the minimum speed, using ascending PID ~-~ 最小上升速度,0表示不启用最小速度,使用上升PID
minimum descending speed, 0 means not enabling the minimum speed, using descending PID ~-~ 最小下降速度,0表示不启用最小速度,使用下降PID
rising speed loop kp ~-~ 上升速度环kp
rising speed loop ki ~-~ 上升速度环ki
rising speed loop kd ~-~ 上升速度环kd
down speed loop kp ~-~ 下降速度环kp
down speed loop ki ~-~ 下降速度环ki
down speed loop kd ~-~ 下降速度环kd
-1 means automatic calculation, when it is a positive number, it means the allowable frame jitter range before and after the encoder ~-~ -1表示自动计算,为正数时表示允许的编码器前后帧抖动范围
-1 means using encoder for feedback, 0 means using driver protocol for feedback, greater than 0 means using timing time for feedback, unit s ~-~ -1表示使用编码器做反馈，0表示使用驱动器协议做反馈，大于0表示使用定时时间做反馈，单位s
-1 means using encoder for feedback, 0 means using driver protocol for feedback, greater than 0 means using timing time for feedback, unit s ~-~ -1表示使用编码器做反馈，0表示使用驱动器协议做反馈，大于0表示使用定时时间做反馈，单位s
Linear Rotating Motor ~-~ 线性旋转电机
motor reduction ratio ~-~ 电机减速比
motor zero speed ~-~ 电机标零速度
max angle ~-~ 最大角度
minimum angle ~-~ 最小角度
zero offset ~-~ 零位偏移量
precision up to position ~-~ 上到位精度
lower precision ~-~ 下到位精度
Max Speed ~-~ 最大速度
max acceleration ~-~ 最大加速度
Max deceleration ~-~ 最大减速度
maximum jerk ~-~ 最大加加速度
minimum ascent speed ~-~ 最小上升速度
minimum descending speed ~-~ 最小下降速度
-1 means automatic calculation, when it is a positive number, it means the allowable frame jitter range before and after the encoder ~-~ -1表示自动计算,为正数时表示允许的编码器前后帧抖动范围
External Encoder ~-~ 外置编码器
external encoder ID ~-~ 外置编码器ID
External Encoder CAN Port ~-~ 外置编码器CAN口
port1 ~-~ 端口1
port2 ~-~ 端口2
External encoder CAN port ~-~ 外置编码器CAN口
none ~-~ 无
Seer controller leading zero ~-~ Seer控制器主导标零
Use the driver to auto-zero ~-~ 使用驱动器自主进行标零
motor DI ~-~ 电机DI
none ~-~ 无
up to place ~-~ 上升到位
ID corresponding to DI ~-~ 对应DI的id
down in place ~-~ 下降到位
ID corresponding to DI ~-~ 对应DI的id
organization ~-~ 机构
organization ~-~ 机构
Basic Settings ~-~ 基础设置
none ~-~ 无
Fork Mechanism ~-~ 货叉机构
Lift Motor ~-~ 举升电机
loading cargo delay time ~-~ 加载货物延时时间
Remove cargo delay time ~-~ 去除货物延时时间
Push Positive Mechanism ~-~ 推正机构
Pushing Motor ~-~ 平推电机
Alignment switch ~-~ 对位开关
Anti-shake time ~-~ 防抖动时间
loading cargo delay time ~-~ 加载货物延时时间
Remove cargo delay time ~-~ 去除货物延时时间
jacking mechanism ~-~ 顶升机构
jacking motor ~-~ 顶升电机
Alignment switch ~-~ 对位开关
Anti-shake time ~-~ 防抖动时间
loading cargo delay time ~-~ 加载货物延时时间
Remove cargo delay time ~-~ 去除货物延时时间
Use IMU for odometry ~-~ 启用IMU参与里程估计
Enable IMU self test ~-~ 启用陀螺仪自检
Time interval threshold for IMU error judgement (s) ~-~ 陀螺仪连续错误的判定时间(s)
Threshold for IMU noise judgement ~-~ 陀螺仪噪声判定阈值
Threshold for IMU error judgement ~-~ 陀螺仪错误判定阈值
Enable skid detection ~-~ 启用打滑检测
Use laser odometer for skid detection ~-~ 启用激光里程计用于打滑检测
Skid detection threshold above which the acceleration error will trigger skid flag (m/s^2) ~-~ 打滑检测的加速度误差阈值(m/s^2)
Skid detection threshold above which the rotation speed error will trigger skid flag (deg/s) ~-~ 打滑检测的角速度误差阈值(deg/s)
Skid detection threshold above which the diffenrentiated displacement error will trigger skid flag (m/s) ~-~ 打滑检测的差分里程计位移误差阈值(m/s)
Skid detection moving average window width for inertial quantities in sample cnts ~-~ 打滑检测的加速度/角速度滑动平均窗口采样数
Skid detection moving average window width for displacement in sample cnts ~-~ 打滑检测的位移滑动平均窗口采样数
Steer angle offset calibration result file ~-~ 舵角偏置标定文件
Bias of accelerometer in X axis ~-~ x轴加速度计偏置
Bias of accelerometer in Y axis ~-~ y轴加速度计偏置
Bias of accelerometer in Z axis ~-~ z轴加速度计偏置
Whether to enable the wheel movement consistency warning ~-~ 启用各轮运动一致性检测
Threshold of wheel movement consistency warning (m/s) ~-~ 各轮运动冲突报警阈值
Warning window width of the motor following error monitor (s) ~-~ 电机跟踪误差监视器警告时间窗口宽度(s)
Error window width of the motor following error monitor (s) ~-~ 电机跟踪误差监视器错误时间窗口宽度(s)
Time delay from the command to the response for the motor following error monitor (s) ~-~ 电机跟踪误差监视器速度响应延时参数(s)
Warning threshold of the motor following error monitor (m/s) ~-~ 电机跟踪误差监视器警告阈值(m/s)
Error threshold of the motor following error monitor (m/s) ~-~ 电机跟踪误差监视器错误阈值(m/s)
Whether set error and stop the vehicle when motor following error occurs ~-~ 当发生电机跟踪误差错误时报错并停止机器人
Whether enable the detailed debug log of the odometer ~-~ 启用里程计调试模式
Whether enable the accumulated differential encoder value mode for pose calculation in odometer ~-~ 在里程计位姿计算时启用编码器差分累加模式
Whether to show the experimental calibration operations ~-~ 启用实验性标定功能
Whether to use advanced calibration types rather than the basic ones ~-~ 启用高级标定类型取代基本标定类型
Calibration debug mode switch ~-~ 启用标定调试输出
Side length of the moving space in laser-odom calibration for differential vehicle (m) ~-~ 差动车激光-里程计标定运动范围边长(m)
Side length of the moving space in laser-odom calibration for steer vehicle (m) ~-~ 单舵轮车激光-里程计标定运动范围边长(m)
Whether to screen out the data sections with higher fitting error in laser-odom calibration ~-~ 是否在激光-里程计标定的分步线性求解过程中剔除不一致数据
Whether to use optimization-based identification method in laser-odom calibration rather than step-by-step linear method ~-~ 在激光-里程计标定中启用基于最优化的求解方法，取代分步线性求解方法
Speed in laser-odom calibration (m/s) ~-~ 激光-里程计标定中机器人的行驶速度(m/s)
Max rotational velocity allowed for differential vehicle in laser-odom calibration (deg/s) ~-~ 激光-里程计标定中机器人的最大旋转速度(deg/s)
How many cycles of movements will the vehicle execute in laser-odom calibration or laser calibration on odometer ~-~ 激光外参标定和激光-里程计标定中标定动作的循环次数
Side length of the moving space in IMU initial calibration (m) ~-~ IMU标定运动范围边长(m)
Speed in IMU initial calibration (m/s) ~-~ IMU标定中机器人的行驶速度(m/s)
Angular speed in IMU initial calibration (deg/s) ~-~ IMU标定中机器人的角速度(deg/s)
Acc and dec in IMU initial calibration (m/s^2), NOT ACTIVE YET ~-~ IMU标定中机器人的加速度(m/s^2)，尚未生效
How many times will the vehicle run forward and backward in IMU initial calibrations ~-~ IMU标定中机器人前后往复行驶的次数
How many pairs of positive and negative rotations (540 degs) will the vehicle execute in IMU initial calibrations ~-~ IMU标定中机器人左右往复旋转(每次540度)的次数
Whether the QR code is orthogonal ~-~ 二维码是否与地面垂直且平齐
Route length of the bi-steer vehicle steer angle offset calibration (m) ~-~ 双舵轮车舵角偏置差标定中机器人行驶距离(m)
Speed in the bi-steer vehicle steer angle offset calibration (m/s) ~-~ 双舵轮车舵角偏置差标定中机器人行驶s速度(m/s)
Route length of the PGV calibration (m) ~-~ PGV标定中的路径长度(m)
Linear speed in PGV calibration (m/s) ~-~ PGV标定的线速度(m/s)
Angular speed in PGV calibration (deg/s) ~-~ PGV标定的角速度(deg/s)
How many times will the vehicle move back and forth in PGV calibration ~-~ PGV标定中前后往复行驶的次数
Route length of the TempSteerOffsetCalib (m) ~-~ 特定模态舵角偏置标定路径长度(m)
Speed of the TempSteerOffsetCalib (m/s), sign determining direction ~-~ 特定模态舵角偏置标定行驶速度(m/s)，符号表示方向
Curvature of the TempSteerOffsetCalib (rad/m), reciprocal of the radius ~-~ 特定模态舵角偏置标定路径曲率(rad/m)，即旋转半径的倒数
Wait time before monitoring the steer angle response (s) ~-~ 舵角范围标定中等待舵角开始响应的时间(s)
Window time for monitoring the steer angle response (s) ~-~ 舵角范围标定中观测窗口的长度(s)
Angle variation tolerance for taking the steer angle response as steady within the window (deg) ~-~ 舵角范围标定中舵角进入稳定状态的判定阈值(deg)
Backstep angle from the steer angle limit in the model file for the steer angle range calibration to start (deg) ~-~ 舵角范围标定中起始角度相对于模型文件描述的舵角范围边界的回退量(deg)
Angular speed for the steer angle range calibration (deg/s) ~-~ 舵角范围标定中舵角变化的速度(deg/s)
How many moves (forward and back) to take that split 180 deg range in roller angle calibration ~-~ 轮辊角标定中往复行驶的次数
Omnidirectional movement distance in roller angle calibration (m) ~-~ 轮辊角标定中每次行驶的距离(m)
Omnidirectional movement speed in roller angle calibration (m/s) ~-~ 轮辊角标定中行驶的速度(m/s)
Arc length for piecewise laser-odometer calibration for steer vehicles (m) ~-~ 分段激光-里程计标定中每段路径的弧长(m)
Sample number of wheel speed in sectional laser-odometer calibration for steer vehicles ~-~ 分段激光-里程计标定中轮速的采样数
Sample number of steer angle in sectional laser-odometer calibration for steer vehicles ~-~ 分段激光-里程计标定中舵角的采样数
Steer angle sampling interval in sectional laser-odometer calibration for steer vehicles (deg) ~-~ 分段激光-里程计标定中舵角的采样间隔(deg)
Minimum wheel speed in sectional laser-odometer calibration for steer vehicles (m/s) ~-~ 分段激光-里程计标定中的最小采样轮速(m/s)
Maximum wheel speed in sectional laser-odometer calibration for steer vehicles (m/s) ~-~ 分段激光-里程计标定中的最大采样轮速(m/s)
Steer angle range bleeding in sectional laser-odometer calibration for steer vehicles (deg) ~-~ 分段激光-里程计标定中舵角采样相较于舵角范围边界的回退量(deg)
Wheel speed resolution in sectional laser-odometer calibration for steer vehicles (m/s) ~-~ 分段激光-里程计标定中轮速采样的最小间隔(m/s)
Steer angle resolution in sectional laser-odometer calibration for steer vehicles (deg) ~-~ 分段激光-里程计标定中舵角采样的最小间隔(m/s)
Differential time for temporal rotation center monitoring ~-~ 旋转中心监视器的窗口时长
Repeated times of the calibration movements in repeated laser-odom calibration ~-~ 重复激光-里程计标定的重复次数
Route length of the bi-steer vehicle mean steer angle offset calibration (m) ~-~ 双舵轮平均舵角标定中的行驶距离(m)
Speed in the bi-steer vehicle mean steer angle offset calibration (m/s) ~-~ 双舵轮平均舵角标定中的行驶速度(m/s)
Route length of PGV-odometer calibration (m) ~-~ PGV-里程计标定中的路径长度(m)
Rotation angle of PGV-odometer calibration (deg) ~-~ PGV-里程计标定中的旋转角度(deg)
Linear speed of PGV-odometer calibration (m/s) ~-~ PGV-里程计标定中的行驶速度(m/s)
Rotational speed of PGV-odometer calibration (deg/s) ~-~ PGV-里程计标定中的旋转速度(deg/s)
How many times will the vehicle run forward and backward in PGV-odometer calibrations ~-~ PGV-里程计标定中前后往复行驶的次数
How many times will the vehicle rotate forward and backward in PGV-odometer calibrations ~-~ PGV-里程计标定中左右往复旋转的次数
Acceration in fork test move (m/s^2) ~-~ 货叉测试动作中的加速度(m/s^2)，符号控制运动方向
Watch window width in fork test move (s) ~-~ 货叉测试动作中的观察窗口宽度(s)
Distance to stop fork test move away from the maxHeight (m) ~-~ 货叉测试动作中与最大高度间的安全距离(m)
Starting height of fork test move (m) ~-~ 货叉测试动作中的起始高度(m)
Max speed of fork test move (m/s) ~-~ 货叉测试动作中的最大速度(m/s)
Speed to navigate to the start height in fork test move (m/s) ~-~ 货叉测试动作中运动到起始高度的速度(m/s)
Width of windowed derivative for fork height (s) ~-~ 货叉测试动作中监视窗口的宽度(s)
Constant speed moving time in deceleration test (s) ~-~ 货叉减速测试动作中匀速运动的时长(s)
TRUE for acceleration response, FALSE for deceleration response ~-~ 货叉测试动作是否为加速测试

motor powered by digital output ~-~ DO控制的电机
motor powered by digital output ~-~ DO控制的电机
type ~-~ 方式
none ~-~ 无
use two do to control ~-~ 互锁类型，使用两个DO分别进行控制
one do for reverse, another for enable ~-~ 使用一个DO换向，一个DO使能
calib direction ~-~ 标零的方向,正向或反向
negative(e.g. jack down) ~-~ 反方向(如顶升向下)
positive(e.g. jack up) ~-~ 正方向(如顶升向上)
type ~-~ 类型
buzzer ~-~ 蜂鸣器
triColorLight ~-~ 三色灯
cruiseLight ~-~ 巡航灯
directionLight ~-~ 方向灯,使用真值表灵活搭配
WST-SM16512PS-DMX512 ~-~ SM16512芯片灯带
private led ~-~ 用户私有灯板
faceUp ~-~ 朝上的面
Look for ICONS or instructions ~-~ 查看图示或说明书
basic ~-~ 基础参数
shape ~-~ 形状
arc ~-~ 扇形
vertex ~-~ 多边形
type ~-~ 类型
none ~-~ 空
collision ~-~ 碰撞条
infrared ~-~ 红外
ultrasonic ~-~ 超声
fallingDown ~-~ 防跌落
func ~-~ 功能
none ~-~ 空
stop ~-~ 停止
slowdown ~-~ 减速
source ~-~ 来源
EMC button ~-~ 急停按钮
externalControl ~-~ 外部控制
motorInfo ~-~ 电机信息
type ~-~ 触发类型
risingEdge ~-~ 上升沿/高电平
fallingEdge ~-~ 下降沿/低电平
func ~-~ 功能
suspendTask ~-~ 挂起任务
resumeTask ~-~ 唤醒任务
cancelTask ~-~ 取消任务
releaseControl ~-~ 释放控制权
recycleControl ~-~ 回收控制权
powerOffDriver ~-~ 驱动器断电
powerOnDriver ~-~ 驱动器上电
openDO ~-~ 打开指定DO
closeDO ~-~ 关闭指定DO
switchToSRCControl ~-~ SRC获取控制
switchToExternalControl ~-~ SRC释放控制
navToTarget ~-~ 导航到指定目标点
resetMotor ~-~ 复位(标零)电机
clearMotorFault ~-~ 清除驱动器错误
toggleDO ~-~ 翻转指定DO
enableMotor ~-~ 使能电机
disableMotor ~-~ 去使能电机
runScript ~-~ 运行脚本
clearErrorCode ~-~ 清除错误码
setErrorCode ~-~ 设置错误码
repowerDriver ~-~ 重上电驱动器
reopenDO ~-~ 重新开关DO
clearMotorEncoder ~-~ 清零驱动器绝对值编码器值
func ~-~ 功能
none ~-~ 无
slowDown ~-~ 减速
stop ~-~ 停止
fallingDown ~-~ 防跌落
brand ~-~ 品牌
BeneWake-TFmini-i ~-~ 北醒单点测距雷达
Elco-OSM4x-485 ~-~ 宜科OSM4x单点激光
port ~-~ 通信接口
rs485 ~-~ rs485接口
basic ~-~ 基础参数
type ~-~ 通信接口
RS485 ~-~ rs485接口
RS232 ~-~ rs232接口
baudrate ~-~ 波特率
fork ~-~ 货叉
measure ~-~ 测量
enable Modbus IO extend module ~-~ 启用 Modbus IO 扩展模块
ip of Modbus IO extend module ~-~ Modbus IO 扩展模块的 IP
port of Modbus IO extend module ~-~ Modbus IO 扩展模块的端口
offset of digital output for Modbus IO ~-~ Modbus IO 扩展模块的 DO 地址偏置
offset of digital input for Modbus IO ~-~ Modbus IO 扩展模块的 DI 地址偏置
number of digital output for Modbus IO ~-~ Modbus IO 扩展模块的 DI 数量
number of digital input for Modbus IO ~-~ Modbus IO 扩展模块的 DO 数量
debug for test speed ~-~ 下发速度调试
debug for IMU ~-~ IMU 调试
astern alarm flag ~-~ 倒车蜂鸣器警报
debug for accelerometer ~-~ 加速度计调试
debug for imu ~-~ 角度调试
debug for odometer ~-~ 里程调试
debug for sonic ~-~ 超声调试
debug for RFID ~-~ RFID 调试
debug for magnetic sensor ~-~ 磁传感器调试
debug for digital input ~-~ DI 调试
debug for encoder ~-~ 编码器调试
debug for Modbus IO ~-~ Modbus IO 调试
debug for PGV ~-~ PGV 调试
PgvPrintOrigData ~-~ 显示pgv原始数据
When switching internal and external control modes, do not consider whether the car body is stopped or not ~-~ 切换内部和外部控制模式时不考虑车体是否停住(可能造成安全隐患,慎重更改)
battery source choosen by soc ~-~ 使用电源芯片的电池电量
max voltage when full percent ~-~ 电量满时电池电压(V)
min voltage when empty percent ~-~ 电量耗尽前电池电压(V)
speed ratio for chassis move ~-~ 底盘速比
fork pressure debug framrate ~-~ 货叉压力传感器log记录频率
print debug counter ~-~ 电机信息log记录频率
return navspeed debug ~-~ 是否打印发布的navspeed消息
buzzer info ~-~ 蜂鸣器调试
use battery internal relay ~-~ 电池内部充电继电器
interlock when jack and walk ~-~ 行走顶升电机互锁
slow time when newspeed timeout triggered ：NewSpeedTimeoutSlowT*20 ms ~-~ newspeed timeout触发后减速时间：NewSpeedTimeoutSlowT*20 ms
enable warninglight ~-~ warninglight输出是否有效
calibration is running ~-~ 标零程序正在运行
whether recoder odometer can frame ~-~ 是否记录原始里程can报文
whether is the status that ready to move ~-~ 是否准备移动标志位
to judge the gyro if flying ~-~ 陀螺仪飘阈值
freq of query for enable and error ~-~ 查询电机使能或报错频率
don't clean error that motor disable or error ~-~ 电机去使能或报错恢复后不清除报警状态
flag for dmx512 led test ~-~ 灯带测试

type ~-~ 类型
number of wheel ~-~ 电机数量
encoder line ~-~ 编码器线束
factor of motor current ~-~ 电机电流因数
passive motor ~-~ 是否是被动电机
Copley-ADP-CANOpen ~-~ copley ADP系列
HLS-LS-Private ~-~ 和利时 LS系列私有
Kinco-FD-CANOpen ~-~ 步科 FD系列
Motec-ARES-CANOpen ~-~ Motec ARES系列
Wellwit-SeerCANOpen ~-~ 井智 私有
Moons-MDX-SeerCANOpen ~-~ 鸣志 MDX系列
Seer-SDMC-Private ~-~ Seer 私有
HLS-LS-CANOpen ~-~ 和利时 LS系列
steer range of curtis ~-~ curtis角度范围
Curtis-1298-DHL ~-~ Curtis-1298-DHL
Curtis-1232-RuiBoTe ~-~ Curtis-1232-RuiBoTe
Curtis-1298-Seer ~-~ Curtis-1298-Seer
Curtis-1232-HeLi ~-~ Curtis-1232-HeLi
Nanotec-AE-CANOpen ~-~ Nanotec AE系列
Curtis-1298-Nuoli ~-~ Curtis-1298-Nuoli
Keya-KYDBL-CANOpen ~-~ 科亚 KYDBL系列
Keya-48150-CANOpen ~-~ 科亚 48150系列
HLS-DS/RS-CANOpen ~-~ 和利时 DS/RS系列
MuXing-IGS-CANOpen ~-~ 牧星 IGS系列
LeiSai-LD5-CANOpen ~-~ 雷赛 LD5系列
Jinling-DDR-CANOpen ~-~ 金陵 DDR系列
Tongyi-IxL-CANOpen ~-~ 同毅 IxL系列
RoboteQ-SeerCanopen ~-~ RoboteQ 私有
Maxon-Canopen ~-~ Maxon
Technosoft-Canopen ~-~ Technosoft
Moons-M2DC-CANOpen ~-~ 鸣志 M2DC系列
Kinco-Stepper-CANOpen ~-~ 步科步进电机
TsinoDynatron-CDA8-CANOpen ~-~ TsinoDynatron-CDA8
Curtis-1234-HangCha ~-~ Curtis-1234-HangCha
AKerMan-Chassis-CANOpen ~-~ 煜禾森阿克曼底盘
ZAPI-Ace2-TianTian ~-~ ZAPI Ace2 天天用
Curtis-1234-ZhiChe ~-~ Curtis-1234-智车
ESTUN-DC10BMG-CANOpen ~-~ 埃斯顿 DC10BMG
JMC-C830RC-CANOpen ~-~ JMC C830RC
MOON-MBDV-CANOpen ~-~ 鸣志 MBDV系列
Keya-48150-2E-CANOpen ~-~ 科亚 48150-2E
AMC-DZCANTE-CANOpen ~-~ AMC DZCANTE
Curtis-1232-Seer-L14 ~-~ Curtis-1232-Seer-L14
Curtis-1232-JiaTeng ~-~ Curtis-1232-JiaTeng
Curtis-1234-Seer ~-~ Curtis-1234-Seer
-1 indicates automatic calculation. A positive number indicates the jitter range of the encoder ~-~ -1表示自动计算,大于0表示编码器抖动的范围
K of dead dealer ~-~ 死区积分器K参数
ratio of external encoder ~-~ 外置编码器比值
factor of external encoder ~-~ 外置编码器系数
encoderline of external encoder ~-~ 外置编码器线数
Battery low voltage error threshold ~-~ 电池低电压error阈值
Battery temperature threshold ~-~ 电池高温阈值
Battery warning Percentage ~-~ 电池低电量warn阈值
Battery error Percentage ~-~ 电池低电量error阈值
Battery shutdown Percentage ~-~ 电池低电量关机阈值
YiHe-XZ-Protocol1363 ~-~ 一合1363协议
PylonTech-RB2450-Protocol1363 ~-~ 派能1363
TopBand-TB4840F-WwPrivate ~-~ 拓邦
Kingor-KGNL001-NLPrivate ~-~ Kingor-KGNL001-NLPrivat
Kingor-TernaryLi-AJPrivate ~-~ Kingor-TernaryLi-AJPrivate
JunDi-MCF-CAN ~-~ JunDi-MCF-CAN
RuiBoTe-MCF-CAN ~-~ RuiBoTe-MCF-CAN
ZhongQi-None-CANOpen ~-~ ZhongQi-None-CANOpen
LiShen-None-Private ~-~ 力神
Fuyuka-MZ-Private ~-~ Fuyuka-MZ-Private
LiPin-Fork-Protocol1363 ~-~ 锂平叉车1363
AnJo-None-Private ~-~ AnJo-None-Private
KuLi-None-Private ~-~ 酷锂
LTW-None-Private ~-~ LTW
HeLi-None-Private ~-~ HeLi-None-Private
HuoKe-200A-Modbus ~-~ 霍克200A
MeiKe-LBHX4880A-Protocol ~-~ MeiKe
BaiWei-Bwbm617-ProtocolA5 ~-~ 百威
MeiKe485-485-Protocol ~-~ MeiKe485
YiDian-None-PrivateCan ~-~ YiDian
RuiSheng-None-PrivateCan ~-~ RuiSheng
DaLi-V1-Protocol ~-~ DaLi-V1-Protocol
foxconn-None-Private ~-~ 富士康
HangCha-None-PrivateCan ~-~ 杭叉
AKerMan-FR-PrivateCan ~-~ 煜禾森阿克曼底盘电池
ZhiChe-None-PrivateCan ~-~ 智车电池
SuRay-485-Private ~-~ 速锐电池
JiKong-485-Private ~-~ 极空电池
JinGe-BMS100-Protocol ~-~ 金鸽BMS
MS-MSPrivate ~-~ MSPrivate
Battery capacity ~-~ 电池容量
by voltage ~-~ 通过电压方式
PGV device ID ~-~ pgv设备id
x ~-~ x
y ~-~ y
z ~-~ z
yaw ~-~ yaw
whether install upside ~-~ 是否正装
unit of x ~-~ x的单位
range of x ~-~ x的范围
unit of y ~-~ y的单位
range of y ~-~ y的范围
blink DO index, -1 repersent disable ~-~ 闪光灯do序号，-1代表不启用
unit of angle ~-~ 角度的范围
P+F-R4-485 ~-~ 倍加福
DaHua-R3051-485 ~-~ 大华
DaBo-PGV-485 ~-~ 达泊
emc by io of driver ~-~ 通过驱动器IO接线的急停
stop and enable driver when emc ~-~ 急停时停止再使能
stop then power off driver when emc ~-~ 急停时停止再关掉继电器
Protocol disable (Do not use this function when enableMotor or disableMotor is configured on the Trigger device) ~-~ 通过驱动器协议，和trigger功能的disableMotor冲突
Curtis-1232-RuiBoTe ~-~ Curtis-1232-RuiBoTe
Curtis-1298-Seer ~-~ Curtis-1298-Seer
differential ~-~ 差速
omni ~-~ 麦轮
basic ~-~ 基础
Curtis-1232e-Triwin ~-~ Curtis-1232e-Triwin
Windcon-VSY15D-CANOpen ~-~ Windcon-VSY15D-CANOpen
walk ~-~ 行走电机
steer ~-~ 转向电机
External encoder ~-~ 外置编码器
Velocity in position mode ~-~ 位置模式下的速度
brand of external encoder ~-~ 外置编码器的品牌
voltage ~-~ 电压
capacity ~-~ 容量
percentageCal ~-~ 百分比
type ~-~ 类型
termination resistor ~-~ 终端电阻
by protocol ~-~ 通过协议
MS-PGV-485 ~-~ MS-PGV-485
recycle the control ~-~ 回收控制权
power off the relay when can error occurs ~-~ 当发生can错误时断开继电器
resume the task ~-~ 继续任务
cancel the task ~-~ 取消任务
can protocol handle ~-~ 手柄协议
Curtis-1232-HeLi ~-~ Curtis-1232-HeLi
terminalResistance ~-~ 终端电阻
up Viscous Speed  ~-~ 上升粘性速度
up Speed Bias ~-~ 上升速度偏差

QR code recognition ~-~ 二维码识别
Basic parameters ~-~ 基础参数
QR code position (x direction) ~-~ 二维码位置（x方向）
QR code position (y direction) ~-~ 二维码位置（y方向）
QR code position (z direction) ~-~ 二维码位置（z方向）
Cargo width ~-~ 货物宽度
Cargo length ~-~ 货物长度
After loading the shelf, will it block the laser? ~-~ 加载货架后，是否会阻挡激光
QR code position (z direction) ~-~ 二维码位置（z方向）
QR code size ~-~ 二维码尺寸
Enable forklift pickup in place switch ~-~ 启用叉车取货到位开关
Enable recognition of back distance ~-~ 启用识别的后退距离
Recognition distance ~-~ 识别的后退距离
Shelf ~-~ 货架
The back distance of the forklift from the identification point, generally the length from the center of the mileage to the bottom of the fork ~-~ 叉车从识别点的后退距离，一般为里程中心到叉底的长度
The distance from the forklift recognition point to the adjustment point ~-~ 叉车识别点到调整点的距离
Extra lift height for the forklift to put the battery ~-~ 叉车放电池的额外抬升高度
Recognition height compensation value ~-~ 识别高度的补偿值
Forklift and battery lateral deviation threshold ~-~ 叉车与电池侧向偏差阈值
Maximum number of adjustments ~-~ 最多调整次数
width ~-~ 宽度
length ~-~ 长度
Identify the offset in the x direction of the coordinate ~-~ 识别坐标x方向的偏移量
Identify the offset in the y direction of the coordinate ~-~ 识别坐标y方向的偏移量
Identify the offset of the coordinate angle ~-~ 识别坐标角度的偏移量
Whether to recognize in real time ~-~ 是否实时识别
Is there a side baffle ~-~ 是否有侧边挡板
Recommended identification distance for identifying shelves ~-~ 识别货架的推荐识别距离
Type of shelf leg ~-~ 货架腿类型
Square ~-~ 方形
Cylindrical ~-~ 圆柱形
Type of shelf leg ~-~ 货架腿类型
Shelf height ~-~ 货架高度
Shelf length ~-~ 货架长度
Shelf width ~-~ 货架宽度
After loading the shelf, will it block the laser? ~-~ 加载货架后，是否会阻挡激光
Located in the global coordinate system ~-~ 位于全局坐标系下
Enable forklift pickup in place switch ~-~ 启用叉车取货到位开关
Enable recognition of back distance ~-~ 启用识别的后退距离
Recognition distance ~-~ 识别的后退距离
Type of shelf leg ~-~ 货架腿类型
Minimum width ~-~ 最小宽度
Maximum width ~-~ 最大宽度
Brand ~-~ 品牌
SRC-800 charging spot ~-~ SRC-800 充电桩
liping charging spot ~-~ 锂平充电桩
Charging spot ~-~ 充电桩
After the forklift is inserted into the battery, the height of the lift again ~-~ 叉车插入电池后，再次抬升的高度
Maximum number of adjustments ~-~ 最多调整次数
whether steer controlled by speed  ~-~ 舵角是否通过速度控制
read timeout for liping charger ~-~ 锂平充电桩读取超时
Minimum send sms message interval for each error code ~-~ 针对每个已配置的报警码，两次发送报警短信时间的最小间隔
Minimum send email interval for each error code ~-~ 针对每个已配置的报警码，两次发送报警邮件时间的最小间隔
Arm GraspLoad: The mb_arm_ctx is NULL ~-~ 机械臂夹爪Load连接错误
Arm GraspLoad timeout ~-~ 机械臂夹爪Load连接超时
Arm GraspUnload: The mb_arm_ctx is NULL ~-~ 机械臂夹爪Unload连接错误
Arm GraspUnload timeout ~-~ 机械臂夹爪Unload连接超时
the program is incomplete, please upload the whole src package again! ~-~ 程序受损，请重新安装
Timeout of push API data (s) ~-~ 19301 连接推送数据的超时时间
The size of 3D laser Beams Sampling (deprecated) ~-~ 3D 激光采样的大小(已弃用)
The step of 3D laser Beams Sampling ~-~ 3D 激光采样的步长
Max Manual V Speed ~-~ 手动控制允许下发的最大速度
WKp value of line patrol PID in rec ~-~ 线路巡检PID在记录中的WKp值
Emergency Time (s) ~-~ 紧急情况时间（秒）
SecondReachAngle(°) ~-~ 第二达到角度（°）
Jerk in manual mode while stopping(m/s^3) ~-~ 手动模式停车时的加加速度（m/s^3）
Angle jerk in manual mode while stopping(°/s^3) ~-~ 手动模式停车时的角度加加速度（°/s^3）
Jerk for spin motor while stopping(°/s^3) ~-~ 停车时旋转电机的加加速度（°/s^3）
Jerk in auto mode while stopping(m/s^3) ~-~ 自动模式停车时的加加速度（m/s^3）
PGV Method. 0: BasedOnCode 1: BasedOnOdo 2: BasedOnOdo with Average Filter 3: BasedOnOdo without Filter ~-~ PGV方法。0：基于代码 1：基于里程 2：基于带平均滤波的里程 3：基于不带滤波的里程
PGV Average Data Time ~-~ PGV平均数据时间
PGV max adjust time ~-~ PGV最大调整时间
Second max adjust time ~-~ 第二最大调整时间
Spin Kp ~-~ 旋转Kp
Spin Ki ~-~ 旋转Ki
Spin Ratio ~-~ 旋转比例
relative anchor x position in pgv coordiante (m) ~-~ PGV坐标系中的相对锚定x位置（米）
relative anchor y position in pgv coordiante (m) ~-~ PGV坐标系中的相对锚定y位置（米）
relative anchor theta in pgv coordiante (degree) ~-~ PGV坐标系中的相对锚定角度（度）
Forklift recognition shelf lateral maximum deviation (m) ~-~ 叉车识别货架侧向最大偏差（米）
Forklift recognition tag lateral maximum deviation (m) ~-~ 叉车识别标签侧向最大偏差（米）
Forklift recognition tag angle maximum deviation (deg) ~-~ 叉车识别标签角度最大偏差（度）
Free navigation min step ~-~ 自由导航最小步长
recovery goods when reboot agv ~-~ 重新启动AGV时恢复货物
ignore Jack Load Error ~-~ 忽略千斤顶负载错误
fork can be manual controlled under charging ~-~ 充电时叉车可以手动控制
steer speed (°/s) ~-~ 转向速度（°/s）
Control Time (s) ~-~ 控制时间（秒）
Slip Warnig time threshold (s) ~-~ 滑动警告时间阈值（秒）
Max acceleration Jerk(m/s^3) in PGV Adjust ~-~ PGV调整中的最大加速度加加速度（m/s^3）
Maximum rotational acceleration Jerk(°/s^3) in PGV Adjust ~-~ PGV调整中的最大旋转加速度加加速度（°/s^3）
DCmdTrackType ~-~ DCmdTrackType
WiredShelfDirThresh ~-~ WiredShelfDirThresh
不采用加速度变化 ~-~ 不采用加速度变化
里程调试 ~-~ 里程调试
Whether enable the detailed log of motor following error monitor ~-~ 是否启用电机跟踪错误监视的详细日志
Whether enable the detailed debug log of the motor following error monitor ~-~ 是否启用电机跟踪错误监视的详细调试日志
Whether disable the odometer and motor following error monitor log when the vehicle is still ~-~ 是否在车辆静止时禁用里程表和电机跟踪错误监视日志
Whether set error and stop the vehicle when linear motor following error occurs ~-~ 是否在线性电机跟踪错误发生时设置错误并停止车辆
Warning window width of the linear motor following error monitor (s) ~-~ 线性电机跟踪错误监视的警告窗口宽度（秒）
Still threshold of the motor following error monitor (m/s) ~-~ 电机跟踪错误监视的静止阈值（m/s）
Whether to log the detail of the motor following error monitor output ~-~ 是否记录电机跟踪错误监视输出的详细信息
enable global points ~-~ 启用全局点
Sleep Time (ms) ~-~ 睡眠时间（毫秒）
Use empty operation for data processing to test movements ~-~ 使用空操作进行数据处理以测试移动
Use parameter consistency calibration ~-~ 使用参数一致性标定
Whether force to use bird's claw shaped route in laser-odometer or laser external calibrations ~-~ 在激光里程计或激光外部标定中是否强制使用鸟爪形路线
How many pairs of forward and backward circles (540 degs) will the vehicle execute in IMU initial calibrations ~-~ 在IMU初始校准中车辆将执行前后旋转(540度)的次数
Steer angle bleed in IMU initial calibrations ~-~ IMU初始标定中的期望转向角
Side length of the moving area in odometer-localization trajectory compare test (m) ~-~ 激光-里程计对比标定时的运动边长
Max linear velocity in odometer-localization trajectory compare test (m/s) ~-~ 激光-里程计对比标定时的最大线速度
Max rotation velocity in odometer-localization trajectory compare test (deg/s) ~-~ 激光-里程计对比标定时的最大角速度
Sampling interval (unit: ms) ~-~ 采样间隔（单位：毫秒）
ProbeCpu loop interval (unit: ms) ~-~ 探测CPU循环间隔（单位：毫秒）
vmstat log flag ~-~ vmstat日志标志
vmstat log frequency (unit: s) ~-~ vmstat日志频率（单位：秒）
IOMonitorDebugFlag ~-~ IOMonitor调试标志
iomonitor log frequency (unit: ms) ~-~ IOMonitor日志频率（单位：毫秒）
iomonitor list number ~-~ IOMonitor列表数量
_iomonitor_read_warn_threshold (unit: kB/s) ~-~ _iomonitor读取警告阈值（单位：千字节/秒）
_iomonitor_write_warn_threshold (unit: kB/s) ~-~ _iomonitor写入警告阈值（单位：千字节/秒）
_iomonitor_read_err_threshold (unit: kB/s) ~-~ _iomonitor读取错误阈值（单位：千字节/秒）
_iomonitor_write_err_threshold (unit: kB/s) ~-~ _iomonitor写入错误阈值（单位：千字节/秒）
SeerRoller error: ~-~ SeerRoller错误：
SeerJack error: ~-~ SeerJack错误：
SeerHook error: ~-~ SeerHook错误：
sound play count is invalid: ~-~ 声音播放计数无效：
sound file does not exist: ~-~ 声音文件不存在：
sound file does not exist, sound file read failed: ~-~ 声音文件不存在，声音文件读取失败：
sound task is sent too frequently ~-~ 声音任务发送频率过高
If allow wheelBaseShiftLength calibration ~-~ 如果允许轮距偏移长度校准
multiSteers ~-~ 多舵轮
dualDiff ~-~ 双差速
id number of power off DO, -1 means that the DO does no exist ~-~ 断电DO的ID编号，-1表示DO不存在
DISensor ~-~ DI传感器
safeMoveCheck ~-~ 安全移动检查
periodRun ~-~ 周期运行
xMin ~-~ x最小值
xMax ~-~ x最大值
yMin ~-~ y最小值
yMax ~-~ y最大值
groupId ~-~ 组ID
laser group ~-~ 激光组
group id ~-~ 组ID
distanceNode group ~-~ 距离节点组
static ~-~ 静态
group id, -1 means all group ~-~ 组ID，-1表示所有组
dynamic ~-~ 动态
motor name ~-~ 电机名称
condition ~-~ 条件
motor ~-~ 电机
parameter ~-~ 参数
position ~-~ 位置
operation ~-~ 操作
value ~-~ 值
pgv ~-~ 位置导引视觉系统
id ~-~ 编号
dispatcherParams ~-~ 调度参数
auto Task ~-~ 自动任务
ForkHeight in load state when agv is away from bin ~-~ AGV离开料箱时的装载状态叉高
ForkHeight in unload stage when agv is away from bin ~-~ AGV离开料箱时的卸载阶段叉高
Check all cargo contact DI ~-~ 检查所有货物接触DI
Forklift cargo detachment switch ~-~ 割台货物分离开关
Enable the inter~-~fork sensor when loading goods ~-~ 装货时启用叉间传感器
Enable fork sensor when unloading cargo ~-~ 卸货时启用叉传感器
DistanceNode in fork tip ~-~ 叉尖的距离节点
disable distanceNode id at load ~-~ 装载时禁用距离节点ID
-1 is not enabled, >0 overwrite the ObsStopDist at load ~-~ -1表示未启用，大于0则在装载时覆盖ObsStopDist
Maximum fork height bias error 52171 threshold. Zero means disable maxHeightBias ~-~ 最大叉高偏差错误52171阈值。零表示禁用maxHeightBias
The maximum time threshold for fork height bias error to occur. The unit is minutes ~-~ 叉高偏差错误发生的最大时间阈值。单位为分钟
Fork down distance with ultrasonic Di ~-~ 通过超声波DI的货叉下降距离
The threshold to judge whether to move horizontally ~-~ 用于判断是否水平移动的阈值
Whether to play audio in only action ~-~ 是否仅在动作中播放声音
cargo DI continuous detection time, after this time is continuously triggered, it is considered successful ~-~ 货物DI连续检测时间，在此时间内连续触发则视为成功
Braking jack motor, when jack motor reaches goal ~-~ 在千斤顶电机达到目标时，制动千斤顶电机
Control method of roller mechanism ~-~ 辊筒机构的控制方法
roller is controlled by PLC or Modbus ~-~ 辊筒由PLC或Modbus控制
roller is controlled by Script ~-~ 辊筒由脚本控制
scriptName ~-~ 脚本名称
whether to reverse ~-~ 是否反转
whether steer controlled by speed ~-~ 转向是否由速度控制
Motor type ~-~ 电机类型
pump and valve ~-~ 泵和阀门
up max acceleration ~-~ 上升最大加速度
up max Deceleration ~-~ 上升最大减速度
up max Jerk ~-~ 上升最大加加速度
up max Speed ~-~ 上升最大速度
down max acceleration ~-~ 下降最大加速度
down max Deceleration ~-~ 下降最大减速度
down max Jerk ~-~ 下降最大加加速度
down max Speed ~-~ 下降最大速度
WKp value of line patrol PID in rec ~-~ 识别时中线巡PID的WKp值
Emergency Time (s) ~-~ 紧急情况时间（秒）
Second Reach Angle (°) ~-~ 第二达到角度（°）
Jerk in manual mode while stopping (m/s^3) ~-~ 手动模式停止时的加加速度（m/s^3）
Angle jerk in manual mode while stopping (°/s^3) ~-~ 手动模式停止时的角度加加速度（°/s^3）
Jerk for spin motor while stopping (°/s^3) ~-~ 停止时旋转电机的加加速度（°/s^3）
Jerk in auto mode while stopping (m/s^3) ~-~ 自动模式停止时的加加速度（m/s^3）
PGV Method. 0: BasedOnCode 1: BasedOnOdo 2: BasedOnOdo with Average Filter 3: BasedOnOdo without Filter ~-~ PGV方法。0：基于代码 1：基于Odo 2：基于Odo带均值滤波 3：基于Odo无滤波
PGV Average Data Time ~-~ PGV平均数据时间
PGV max adjust time ~-~ PGV最大调整时间
Second max adjust time ~-~ 第二最大调整时间
Spin Kp ~-~ 随动Kp
Spin Ki ~-~ 随动Ki
Spin Ratio ~-~ 随动比率
relative anchor x position in pgv coordinate (m) ~-~ PGV坐标系中的相对锚点x位置（米）
relative anchor y position in pgv coordinate (m) ~-~ PGV坐标系中的相对锚点y位置（米）
relative anchor theta in pgv coordinate (degree) ~-~ PGV坐标系中的相对锚点θ位置（度）
Forklift recognition shelf lateral maximum deviation (m) ~-~ 堆垛机识别货架侧向最大偏差（米）
Forklift recognition tag lateral maximum deviation (m) ~-~ 堆垛机识别标签侧向最大偏差（米）
Forklift recognition tag angle maximum deviation (deg) ~-~ 堆垛机识别标签角度最大偏差（度）
Free navigation min step ~-~ 自由导航最小步长
recovery goods when reboot agv ~-~ 重新启动AGV时的货物恢复
ignore Jack Load Error ~-~ 忽略千斤顶载荷错误
fork can be manually controlled under charging ~-~ 充电时可手动控制叉
steer speed (°/s) ~-~ 转向速度（°/s）
Control Time (s) ~-~ 控制时间（秒）
Slip Warning time threshold (s) ~-~ 打滑警告时间阈值（秒）
Max acceleration Jerk (m/s^3) in PGV Adjust ~-~ PGV调整中的最大加加速度（m/s^3）
Maximum rotational acceleration Jerk (°/s^3) in PGV Adjust ~-~ PGV调整中的最大旋转加加速度（°/s^3）
DCmdTrackType ~-~ DCmdTrackType
WiredShelfDirThresh ~-~ 有线货架方向阈值
Lift motor name ~-~ 升降电机名
Lsift sensor name ~-~ 顶升升降传感器名称
Highest position of lift ~-~ 升降最高位置
Lowest position of lift ~-~ 升降最低位置
Chassis motor name ~-~ 底盘电机名称
Chassis lift sensor name ~-~ 底盘升降传感器名称
x speed ratio switching distance ~-~ x 速比切换距离
x speed ratio ~-~ x 速比
y speed ratio switching distance ~-~ y 速比切换距离
y speed ratio ~- ~y 方向速比
y direction motor speed inverse ~-~ y 方向电机速度逆
Lift reach distance ~-~ 升降到点精度
poweroffDO parameters ~-~ 关闭 DO 的参数
When a dynamic obstacle is in this area, the corresponding DO state is triggered. ~-~ 当动态障碍物在这个区域内,触发相应的DO状态
Minimum value in the x-direction of the detection area ~-~ 检测区域 x 最小值
Minimum value in the y-direction of the detection area ~-~ 检测区域 y 最小值
Maximum value in the x-direction of the detection area ~-~ 检测区域 x 最大值
Maximum value in the y-direction of the detection area ~-~ 检测区域 y 最大值
Id of the opened Do, -1 means not enabled ~-~ 被打开Do的id, -1表示不启用
ForkHeight in unload stage when agv is away form bin ~-~ 当搬运车离开料仓时，卸载阶段的货叉高度
Check all cargo contack DI ~-~ 检查所有货物接触 DI
Enable the inter-fork sensor when loading goods ~-~ 装载货物时启用叉间传感器
The maximum time threshold for fork height bias error to occur.The unit is minutes ~-~ 货叉高度偏差错误发生的最大时间阈值。单位为分钟
Cargo containers ~-~ 货物容器
Braking jack motor, when jack motor reachs goal. ~-~ 当顶升电机到位时，制动顶升电机
roller is controlled by PLC or modubus ~-~ 辊筒由PLC或Modbus控制
internal error ~-~ 内部错误
resource exhaustion ~-~ 资源耗尽
lua error ~-~ Lua错误
map parse error ~-~ 地图解析错误
map load error ~-~ 地图加载错误
map is too large ~-~ 地图过大
map is empty ~-~ 地图为空
map meta error ~-~ 地图元数据错误
map resolution is illegal ~-~ 地图分辨率非法
map format invalid ~-~ 地图格式无效
mobilerobots path error ~-~ 移动机器人路径错误
mobilerobots init error ~-~ 移动机器人初始化错误
mobilerobots register error ~-~ 移动机器人注册错误
unsupported robot motion model ~-~ 不支持的机器人运动模型
can not find mobilerobots dll ~-~ 找不到mobilerobots动态链接库
hardware connect error ~-~ 硬件连接错误
dsp firmware model can not get ~-~ 无法获取DSP固件模型
subsystem error ~-~ 子系统错误
network connection error ~-~ 网络连接错误
firmware version too low ~-~ 固件版本过低
robot modle param config error ~-~ 机器人模型参数配置错误
gyro original data error ~-~ 陀螺仪原始数据错误
battery level is too low and robot will shut down ~-~ 电池电量过低，机器人将关闭
temperature of battery is too high ~-~ 电池温度过高
controller voltage lower than the controller rated voltage, controller will shutdown after ~-~ 控制器电压低于额定电压，控制器将在之后关闭
src800 sdcard error ~-~ src800 SD卡错误
src800 swap error ~-~ src800交换错误
RBK has exited abnormally. Please restart the robot to recover. ~-~ RBK异常退出。请重新启动机器人以恢复。
mode is not activated ~-~ 模式未激活
robot model uninitialized ~-~ 机器人模型未初始化
src800 activation has problem ~-~ src800激活存在问题
steerOffsetFile's path doesn't exist! ~-~ steerOffsetFile的路径不存在！
run taskList error ~-~ 运行任务列表错误
robot model uninitialized, can not upload ~-~ 机器人模型未初始化，无法上传
points with the same id number in the map ~-~ 地图中具有相同ID编号的点
less than 3 reflectors detected error ~-~ 检测到不到3个反射器错误
rbk_laser_loc is not actived, please activate it ~-~ rbk_laser_loc未激活，请激活它
roller error ~-~ 辊筒错误
roller or jack or hook disconnected ~-~ 辊筒、千斤顶或吊钩断开连接
jack error ~-~ 千斤顶错误
hook error ~-~ 吊钩错误
GoodsId isn't same. ~-~ 货物ID不同。
arm disconnected ~-~ 手臂断开连接
arm error ~-~ 手臂错误
arm protective stopped ~-~ 手臂保护停止
arm emergency stopped ~-~ 手臂紧急停止
arm normal error ~-~ 手臂正常错误
arm internal error ~-~ 手臂内部错误
arm internal notice ~-~ 手臂内部通知
arm internal warning ~-~ 手臂内部警告
arm bintask error ~-~ 手臂二进制任务错误
device check error ~-~ 设备检查错误
olam lose laser data ~-~ OLAM丢失激光数据
pf laser data invalid ~-~ PF激光数据无效
internal laser error ~-~ 内部激光错误
please restart laser, get internal Error with Nanosick ~-~ 请重新启动激光，使用Nanosick获取内部错误
cannot connect sick nano laser with same port ~-~ 无法使用相同端口连接Sick Nano激光器
laser config param is wrong ~-~ 激光配置参数错误
can't connect with laser ~-~ 无法连接激光器
laser data invalid ~-~ 激光数据无效
localization module cannot get laser data ~-~ 定位模块无法获取激光数据
cannot receive laser data from udp ~-~ 无法从UDP接收激光数据
please set front laser as use for localization ~-~ 请将前置激光器设置为用于定位
please set back laser as use for localization ~-~ 请将后置激光器设置为用于定位
odo data lost ~-~ 丢失里程数据
Switch map error in current station point ~-~ 在当前站点切换地图错误
time synchronization error ~-~ 时间同步错误
ReferenceArea is blocked ~-~ 参考区域被阻塞
imu error ~-~ IMU错误
motor driver connection error ~-~ 电机驱动器连接错误
ultrasonic error ~-~ 超声波错误
RFID reader error ~-~ RFID读卡器错误
magnetic 0 tracker error ~-~ 磁0跟踪器错误
magnetic 1 tracker error ~-~ 磁1跟踪器错误
controller net down ~-~ 控制器网络断开
dioboard net down ~-~ 数字输入输出板网络断开
seer dio heart beat loss ~-~ SEER DIO心跳丢失
low task frequency ~-~ 任务频率过低
Don't set DO when movetask unreleased DO ~-~ 当movetask未释放DO时不要设置DO
robot fall down ~-~ 机器人摔倒
DSPChassis modbus IO error ~-~ DSP底盘Modbus IO错误
controller under voltage seriously ~-~ 控制器严重欠压
controller over voltage seriously ~-~ 控制器严重过压
PGV connection error ~-~ PGV连接错误
PGV info with mismatched device id ~-~ PGV信息与不匹配的设备ID
Weighing device connect timeout ~-~ 称重设备连接超时
motor GVDD over voltage ~-~ 电机GVDD过压
motor FET over current ~-~ 电机FET过流
motor over temperature ~-~ 电机过温
motor VDD under voltage ~-~ 电机VDD欠压
motor error see log ~-~ 电机错误，请查看日志
chassis new speed timeout ~-~ 底盘新速度超时
steer angle overflow ~-~ 转向角溢出
fork encode connection error ~-~ 叉编码器连接错误
steer wheelbase is too small ~-~ 转向轮距太小
lift safe control trigger ~-~ 升降安全控制触发
model config error ~-~ 模型配置错误
walking jack motor interlock ~-~ 步行千斤顶电机互锁
robot received an illegal speed ~-~ 机器人接收到非法速度
Fork unload fail. Goods are in the goal. ~-~ 卸货失败。货物在目标位置。
Fork Goods Missing. Cannot Detect Goods in the fork ~-~ 货叉上缺货。无法检测到叉上的货物
Error in Velocity Decomposition ~-~ 速度分解错误
Fork Cannot load again. ContactDi is True. ~-~ 货叉不能再次装载。ContactDi为True。
Fork is over time ~-~ 叉已超时
ReachDI is true but AGV is not in the goal. ~-~ ReachDI为真，但AGV不在目标位置。
AGV is in the goal but ReachDI is false. ~-~ AGV在目标位置，但ReachDI为假。
ContactDi doesn't detect Goods! ~-~ ContactDi未检测到货物！
No enough 3D pointCloud in current map, please check or not use 3DLocalization with Current Laser ~-~ 当前地图中没有足够的3D点云，请检查是否使用当前激光器进行3D定位
Goods on the fork is overweight. ~-~ 叉上的货物超重。
The bias between the current fork height and the target value is too much. ~-~ 当前叉高度与目标值之间的偏差太大。
Jack Cannot Load Again. ~-~ 千斤顶无法再次装载。
robot is blocked ~-~ 机器人被阻挡
robot out of path ~-~ 机器人偏离路径
auto charge failed ~-~ 自动充电失败
charge path direction error ~-~ 充电路径方向错误
chargerspot status error ~-~ 充电点状态错误
3D camera disconnected ~-~ 3D相机断开连接
cannot receive IFM data ~-~ 无法接收IFM数据
cannot connect with locCamera ~-~ 无法连接到locCamera
too low confidence of localization ~-~ 定位置信度过低
Cannot detect tag after some distance ~-~ 一段距离后无法检测到标签
Cannot navigation before confirming localization ~-~ 在确认定位之前无法导航
hook has an error ~-~ 钩子出现错误
battery connect error during charging ~-~ 充电过程中电池连接错误
disconnect from RoboRoute ~-~ 与RoboRoute断开连接
button timeout ~-~ 按钮超时
RoboRoute command error ~-~ RoboRoute命令错误
battery level is too low to move ~-~ 电池电量过低无法移动
low reach accuracy ~-~ 低达到精度
cannot find a feasible path ~-~ 找不到可行路径
cannot find target id ~-~ 无法找到目标ID
path planning failed ~-~ 路径规划失败
unsupported navigation method ~-~ 不支持的导航方法
charge failed but not set pre~-~point ~-~ 充电失败但未设置预充电点
motion planning failed ~-~ 运动规划失败
cannot find magstripe ~-~ 找不到磁条
stay in forbidden area ~-~ 停留在禁止区域
destination has obstacles ~-~ 目的地有障碍物
cannot find patrol route ~-~ 找不到巡逻路线
cannot find charge point ~-~ 找不到充电点
DO or DI area overlap ~-~ DO或DI区域重叠
go into shelf failed ~-~ 进入货架失败
current pos has obstacles ~-~ 当前位置有障碍物
charger problem! ~-~ 充电器问题！
charger tcp connection problem! ~-~ 充电器TCP连接问题！
Detect Skid and stop ~-~ 检测到打滑并停止
gnss serial problem! ~-~ GNSS串口问题！
RTK Base serial problem! ~-~ RTK基站串口问题！
gowithfork failed. ~-~ 跟随叉失败。
module or motor control error ~-~ 模块或电机控制错误
upLimit or DownLimit error ~-~ 上限或下限错误
third~-~party error ~-~ 第三方错误
no shelf ~-~ 没有货架
a shelf already there ~-~ 已经有一个货架
motor following error ~-~ 电机跟随错误
motor calibrate timeout ~-~ 电机校准超时
src can not switch mode while moving ~-~ 在移动过程中无法切换SRC模式
motor do not support 'driver protocol EMC' ~-~ 电机不支持“驱动器协议EMC”
DOMotor calibrate ~-~ DO电机校准
DOMotor limit DI triggered ~-~ DO电机限位DI触发
distanceSensor connect timeout ~-~ 距离传感器连接超时
battery timeout error ~-~ 电池超时错误
rec failed! ~-~ 录制失败！
blocked in calibrating ~-~ 在校准过程中被阻挡
The pallet is out of the right position! ~-~ 托盘位置不正确！
motor following monitor init error ~-~ 电机跟随监视器初始化错误
odometer could not be initialized due to model error ~-~ 由于模型错误，里程计无法初始化
script error ~-~ 脚本错误
modbusArm error ~-~ ModbusArm错误
MinSignalLevelAvailable is smaller than MinSignalLevelKeep ~-~ MinSignalLevelAvailable小于MinSignalLevelKeep
motor no response ~-~ 电机无响应
quaternion of IMU pose is non~-~unit, please recalibrate the IMU ~-~ IMU姿态的四元数不是单位四元数，请重新校准IMU
controller voltage lower than the controller rated voltage ~-~ 控制器电压低于控制器额定电压
Scanner devName is not exist ~-~ 扫描仪devName不存在
Gripper need to be calibration ~-~ 夹爪需要校准
IO monitor write speed too higher than normal ~-~ IO监视器写入速度高于正常水平
MagneticSensor connection error ~-~ 磁性传感器连接错误
RFIDSensor connection error ~-~ RFID传感器连接错误
joystick error ~-~ 操纵杆错误
battery error ~-~ 电池错误
temperature sensor error ~-~ 温度传感器错误
motor overspeed ~-~ 电机过速
controller emergency stop ~-~ 控制器紧急停止
task list is executing ~-~ 任务列表正在执行
sonic off line ~-~ 超声波离线
little low task frequency ~-~ 任务频率稍低
controller under voltage ~-~ 控制器欠压
controller over voltage ~-~ 控制器过压
timestamp error ~-~ 时间戳错误
driver emergency stop ~-~ 驱动器紧急停止
jitter occurs when robot is stationary ~-~ 机器人静止时出现抖动
RS485 hardware error ~-~ RS485硬件错误
DO hardware error ~-~ DO硬件错误
reflectors in map not enough ~-~ 地图中的反射器不足
less than 3 reflectors detected ~-~ 检测到不到3个反射器
reflectors match failed, please set right init pose ~-~ 反射器匹配失败，请设置正确的初始姿势
abnormal task frequency ~-~ 异常任务频率
abnormal can data ~-~ 异常CAN数据
which driver emergency stop ~-~ 哪个驱动器紧急停止
which driver have error code ~-~ 哪个驱动器有错误代码
no jack motor in model file ~-~ 模型文件中没有千斤顶电机
DI status is wrong ~-~ DI状态错误
devName of serial port is used more than 1 times ~-~ 串口的devName使用了多次
cannot connect with camera ~-~ 无法连接相机
detect two tag with same ID ~-~ 检测到两个相同ID的标签
Tag cannot be Seen, please enable PGV with Localization or adjust Localization ~-~ 无法看到标签，请启用带有定位的PGV或调整定位
battery report warning ~-~ 电池报告警告
mushiny led timeout ~-~ Mushiny LED超时
external control warning ~-~ 外部控制警告
PGV cannot find codes ~-~ PGV找不到代码
please clean laser, get Contamination Error with Nanosick ~-~ 请清洁激光，使用Nanosick获取污染错误
Steer Range Doesn't Current Motion Planning ~-~ 转向范围与当前运动规划不符
DSP reconfiguring ~-~ DSP正在重新配置
please check pallet detection file, wrong config ~-~ 请检查托盘检测文件，配置错误
fork is in charging. Cannot move it in manual mode ~-~ 叉正在充电。无法在手动模式下移动它
charge failed and go to pre~-~point ~-~ 充电失败并返回预定点
battery level is less than warning level ~-~ 电池电量低于警告级别
Caution：robot is blocked ~-~ 注意：机器人被阻挡
Ignoring Task caused by DISensor ~-~ 忽略由DISensor引起的任务
imu noise is too large ~-~ IMU噪声太大
motor status report ~-~ 电机状态报告
newspeed timeout handle status ~-~ 新速度超时处理状态
detect skid, check configure of model ~-~ 检测到打滑，请检查模型配置
DOMotor is calibrating ~-~ DO电机正在校准
reset motor should in state when all motors are stopped ~-~ 重置电机应该在所有电机停止时进行
The data in RGV distanceSensor is invalid ~-~ RGV距离传感器中的数据无效
The RGV cannot move y direction with lift up ~-~ RGV不能在升降时沿y方向移动
gnss config warning ~-~ GNSS配置警告
gnss cannot get rtcm msg ~-~ GNSS无法获取RTCM消息
RTK Base cannot receive data from uart ~-~ RTK基站无法从UART接收数据
RTK Base http server warning ~-~ RTK基站HTTP服务器警告
RTK Base cannot offer rtcm data in config mode ~-~ RTK基站无法在配置模式下提供rtcm数据
Call Service error! ~-~ 调用服务错误！
third~-~party warning ~-~ 第三方警告
rec fail ~-~ 录制失败！
RouteProtocolVersion is modified and it takes effect after reboot ~-~ RouteProtocolVersion已修改，在重启后生效
The robot is in the dispatching state. If you need to control, please regain control and go offline during dispatching. ~-~ 机器人处于派工状态。如果需要控制，请在派工期间重新获得控制并脱机。
rbk_fork is not activated ~-~ rbk_fork未激活
rbk_pallet is not activated ~-~ rbk_pallet未激活
rbk_pgv_loc is not activated ~-~ rbk_pgv_loc未激活
rbk_tag_nav is not activated ~-~ rbk_tag_nav未激活
rbk_shelf is not activated ~-~ rbk_shelf未激活
rbk_spin is not activated ~-~ rbk_spin未激活
rbk_reflector is not activated ~-~ rbk_reflector未激活
rbk_3dcamera is not activated ~-~ rbk_3dcamera未激活
rbk_dynamic_nav is not activated ~-~ rbk_dynamic_nav未激活
rbk_roaming is not activated ~-~ rbk_roaming未激活
rbk_script is not activated ~-~ rbk_script未激活
src800 feature is not activated ~-~ src800功能未激活
feature not belong src800 should not be activated ~-~ 不属于src800的功能不应该被激活
rbk_laser_loc is not activated ~-~ rbk_laser_loc未激活
wifi_scan error ~-~ WiFi扫描错误
IMU has NOT been calibrated while the skid detection is enabled ~-~ 打滑检测启用时IMU尚未校准
Odometer being unreliable because of wheel movements inconsistency ~-~ 由于轮子运动不一致，里程计不可靠
motor following warning ~-~ 电机跟随警告
Elco timeout warning ~-~ Elco超时警告
controller voltage higher than the controller rated voltage ~-~ 控制器电压高于控制器额定电压
IO monitor write speed higher than normal ~-~ IO监视器写入速度高于正常水平
odometer jump ~-~ 里程计跳动
detect skid, and use laser odo ~-~ 检测到打滑，使用激光里程计
cannot detect tag or pallet, please check recoFile configure or camera pose ~-~ 无法检测到标签或托盘，请检查recoFile配置或相机姿势
file system error ~-~ 文件系统错误
param system error ~-~ 参数系统错误
database error ~-~ 数据库错误
play audio error ~-~ 播放音频错误
gyro calibration completed ~-~ 陀螺仪校准完成
json conversion error ~-~ JSON转换错误
robot moved at gyro calibration ~-~ 陀螺仪校准时机器人移动
self checking failed ~-~ 自检失败
gyro_calibration_acked ~-~ 陀螺仪校准已确认
gyro is fly after calibration ~-~ 校准后陀螺仪飞行
motor hall encoder mismatch ~-~ 电机霍尔编码器不匹配
motor current sum not zero ~-~ 电机电流之和不为零
motor hall error ~-~ 电机霍尔错误
motor dc bus low 15 ~-~ 电机直流母线电压低15
gyro calibration block speed ~-~ 陀螺仪校准阻挡速度
fork target too high ~-~ 叉齿目标太高
fork target too low ~-~ 叉齿目标太低
robot moved before gyro calibration ~-~ 陀螺仪校准前机器人移动
Motor Cmd's num doesn't match with MotInfo's ~-~ 电机命令数与MotInfo不匹配
Check all cargo contack DI ~-~ 检查所有货物接触DI
Enable the inter-fork sensor when loading goods ~-~ 装货时启动叉之间的传感器
disable distanceNode id at load  ~-~ 在负载处禁用distanceNode ID
The maximum time threshold for fork height bias error to occur.The unit is minutes ~-~ 发生叉高偏差错误的最大时间阈值。单位是分钟
fork down distance with ultrasonic Di ~-~ 用超声波Di进行叉下距离
Braking jack motor, when jack motor reachs goal. ~-~ 当千斤顶电机达到目标时刹车
roller is controlled by PLC or modubus ~-~ 滚筒由PLC或modubus控制
rbk_laser_loc is not actived, please active it ~-~ rbk_laser_loc未激活，请激活它
controller under voltage seriourly ~-~ 控制器电压严重不足
controller over voltage seriourly ~-~ 控制器电压过高严重
motor VDD under voltege ~-~ 电机VDD电压过低
ReachDI is true but AGV is not int the goal. ~-~ ReachDI是真实的，但AGV不在目标中。
AGV is in the goal but reachDI is false. ~-~ AGV在目标中，但reachDI是假的。
No enough 3D pointCloud in current map,please check or not use 3DLocalization with Current Laser ~-~ 当前地图中3D点云不足，请检查或者不使用当前激光进行3D定位
Goods on the fork is over weight. ~-~ 叉上的货物超重
can not find a feasible path ~-~ 找不到可行的路径
can not find target id ~-~ 找不到目标id
charge failed but not set pre-point ~-~ 充电失败但未设置预设点
can not find magstripe ~-~ 找不到磁条
can not find patrol route ~-~ 找不到巡逻路线
can not find charge point ~-~ 找不到充电点
third-party error ~-~ 第三方错误
quaternion of IMU pose is non-unit, please recalibrate the IMU ~-~ IMU位姿的四元数是非单位的，请重新校准IMU
abnormal sonic data ~-~ 异常声波数据
Tag cannot be Seen,please enable PGV with Localization or adjustLocalization ~-~ 无法看到标签，请启用定位的PGV或调整定位
DSP reconfiging ~-~ DSP正在重新配置
charge failed and go to pre-point ~-~ 充电失败并前往前置点
third-party warning ~-~ 第三方库警告

lrm use slam in rbk ~-~ 局部地图更新是否启用SLAM
lrm time gap between current task and last task (s) ~-~ 局部地图更新两次建图的最小时间间隔（单位秒）
lrm save submap threshold ~-~ 局部地图更新建图之后的评价标准
lrm use nav pose threshold ~-~ 局部地图更新使用定位位置的置信度门限
lrm use optimization ~-~ 局部地图更新是否启用将定位姿态作为图优化单边
lrm max range ~-~ 局部地图更新建图时激光最大扫描距离，单位米
lrm angle threshold ~-~ 局部地图更新轨迹对齐时选取建图轨迹的角度阈值，单位角度
lrm distance threshold ~-~ 局部地图更新轨迹对齐时选取建图轨迹的距离阈值，单位米
lrm use icp ~-~ 局部地图更新轨迹对齐是否使用icp

GNSS log dual antenna data to rawmap ~-~ 是否记录双天线数据到rawmap文件

update mode info record ~-~ 更新模式信息
Use laser undistortioni ~-~ 是否使用雷达去畸变
Use optical motion track localization ~-~ 是否使用光学运动轨迹定位
Using third-party location positioning data ~-~ 使用第三方定位数据
use RTK Localization ~-~ 是否使用RTK定位
rtk particles weight ~-~ RTK粒子权重
3D Localization Type(Need Reboot) ~-~ 3D定位类型(需要重新启动)
3D Localization weight ~-~ 3D定位权重
3D Points DownSample Size ~-~ 3D点下采样参数
NDT Resolution ~-~ NDT分辨率
NDT Update Time Thd(ms) ~-~ NDT更新数据阈值(ms)
3D Score Distance ~-~ 3D打分阈值距离
Pat Log Skip ~-~ 记录日志间隔时间
enable skid detect ~-~ 使能打滑检测
enable feature loc ~-~ 使能特征定位
Features Valid Range ~-~ 特征有效范围
Features Loc Rotate Thd ~-~ 特征定位旋转阈值
Particle extra move radius (mm) ~-~ 粒子扩散额外半径(毫米)
Particle extra move angle (deg) ~-~ 粒子扩散额外角度(度)
check if force extra move ~-~ 检查是否强制额外移动
use laser rssi to calculate center ~-~ 是否使用激光强点计算反光柱中心
Reflector Localization weight ~-~ 反光柱定位权重
Whether to use reflector triangulation ~-~ 是否使用反光柱三角定位
automatic localization in Tag ~-~ Tag中的自动定位
The particle move angle in low speed ~-~ 低速粒子移动角度范围
whether to record all laser data for loc ~-~ 是否记录定位的所有激光数据
reflector relocation distance ~-~ 反光柱重定位中使用的反光柱范围阈值
reflector relocation threshold ~-~ 反光柱重定位误差阈值
run period time(ms) ~-~ 运行周期时间（ms）
whether to Use OpenCL with PF ~-~ 是否使用OpenCL版本的粒子滤波定位
whether to Use OpenCL with SLAM ~-~ 是否使用OpenCL版本的SLAM定位
Gauss dist for gridMap ~-~ 栅格地图的高斯距离
reflector relocation ICP distance ~-~ 反光柱重定位ICP阈值
reflector localization ICP distance ~-~ 反光柱定位ICP阈值

OM All lasers are used for mapping ~-~ 建图记录器是否记录所有用于定位的激光
OM log number in one zip file ~-~ 建图记录器每包有多少帧激光数据
OM enable laser undistort ~-~ 建图记录器是否启用激光运动补偿
OM imu cnt for each lidar need to record ~-~ 建图记录器每多少个IMU数据记录一帧多线激光数据
OM use mid360 for mapping or not ~-~ 建图记录器是否开启mid360数据记录模式

step ~-~ 步长
minAngle ~-~ 最小角度
maxAngle ~-~ 最大角度
maxRange ~-~ 最大有效距离
max range of laser ~-~ 激光点最大有效距离
upside ~-~ 正装
useForLocalization ~-~ 定位
3DLocalization ~-~ 3D定位
3DObstacleDetection ~-~ 3D障碍物检测
useForBinDetection ~-~ 库位检测
laser ~-~ 雷达
use for 3D obstacle detection ~-~ 用于3D障碍物检测
use laser for bin detection ~-~ 使用雷达检测库位
removedArea ~-~ 已移除区域
useAreaRemove ~-~ 区域移除
use for removing areas ~-~ 用于移除区域
areaStartAngle ~-~ 起始检测角度
area_start_angle ~-~ 起始检测角度
areaEndAngle ~-~ 终止检测角度
area_end_angle ~-~ 终止检测角度
minValidRange ~-~ 最小有效区域
scanFrequency ~-~ 扫描频率
Laser release frame rate ~-~ 雷达预置帧率
sampleSizePerScan ~-~ 单帧采样点数
Number of laser points per frame ~-~ 单帧激光点数
Filtering parameters ~-~ 滤波参数
Baud rate ~-~ 波特率
IPconnect ~-~ IP连接
Serial port to network port ~-~ 串口转网口
Display maximum RSSI ~-~ 显示最强信号强度值
TimeServerIP ~-~ 时间服务器IP
Timestamp server address ~-~ 时间服务器IP地址
NTPUpdateTime ~-~ NTP更新时间
Time synchronization period (s) ~-~ 时间同步周期(s)
LaserRecordInterval ~-~ 激光记录间隔
Laser data recording time interval (s) ~-~ 激光记录间隔(s)
SimulateMaxRange ~-~ 激光最大有效射程
max range of laser ~-~ 激光最大有效检测范围
sleep time ~-~ 休眠时间
DataLostTimeThd ~-~ 丢帧可允许阈值时间
Data lost time thd(ms) ~-~ 数据丢失可允许的最小阈值时间(ms)

LS Laser line segment debugging ~-~ 激光分割 有效点云的最小数量
LS Effective RSSI Threshold ~-~ 激光分割 有效强点阈值
LS Minimum number of point cloud clusters ~-~ 激光分割 最小聚类点云个数
LS Spilt Threshold ~-~ 激光分割 分割门限
LS Valid Leg Range Threshold ~-~ 激光分割  距离车体多少范围的激光是有效的(x方向)，如果是后置激光把该值调成负数
LS Valid Leg Threshold ~-~ 激光分割 有效人腿门限
LS Valid Leg Angle Threshold ~-~ 激光分割 有效人腿角度门限
LS Valid Shelf Angle Range ~-~ 激光分割 有效货架角度范围
LS Wired Shelf Dir Threshold ~-~ 激光分割 有效货架朝向门限
LS Shelf Extra Dist ~-~ 激光分割 货架额外距离
LS Use Reflector For Detect Shelf ~-~ 激光分割 使用反光贴检测货架
LS Use Laser Frame Number ~-~ 激光分割 使用的激光帧数
LS Filter Min Angle ~-~ 激光分割 过滤最小角度
LS Filter Max Angle ~-~ 激光分割 过滤最大角度
LS Filter Window ~-~ 激光分割 过滤窗口大小
LS Filter Neighbours ~-~ 激光分割 过滤的近邻
LS Valid Shape X ~-~ 激光分割 有效形状X
LS Valid Shape Bias ~-~ 激光分割 有效形状偏置
LS Valid Shape Line Threshold ~-~ 激光分割 有效形状线门限
LS Valid Shape Distance Threshold ~-~ 激光分割 有效形状距离门限
LS Valid Shape Line Split Threshold ~-~ 激光分割 有效形状线分割门限
LS Valid Shape Valid Shelf Angle ~-~ 激光分割 有效形状货架角度
LS Number of Shape Inspections ~-~ 激光分割 形状检测个数
LS The Least Points On The Line Segment ~-~ 激光分割 线分割最小点数
LS Valid Fork Line Merge Threshold ~-~ 激光分割 Fork Line合并门限
LS Min Pallet Threshold ~-~ 激光分割 栈板识别最小门限
LS Max Pallet Threshold ~-~ 激光分割 栈板识别最大门限
LS Test Laser Seg ~-~ 激光分割 激光分割测试
LS Has Called Rear Laser Pallet Detection Service ~-~ 激光分割 调用后激光栈板检测服务
LS Predict Distance For Rear Laser Detect Pallet ~-~ 激光分割 后激光栈板检测预测距离
LS Least Thresh For Rear Laser Detect Pallet ~-~ 激光分割 后激光栈板检测点到直线距离的最小阈值
LS Min Line Length For Rear Laser Detect Pallet ~-~ 激光分割 后激光栈板检测提取出的直线最小长度
LS Seed Line Points For Rear Laser Detect Pallet ~-~ 激光分割 后激光栈板检测种子线段包含的激光数
LS Min Line Points For Rear Laser Detect Pallet ~-~ 激光分割 后激光栈板检测提取出的直线包含的最小激光点个数
LS Predict Distance For Laser Line ~-~ 激光分割 提取激光直线预测点到真实点之间距离的最小值
LS Least Threshold For Laser Line ~-~ 激光分割 提取激光直线点到直线距离的最小阈值
LS Min Line Length For Laser Line ~-~ 激光分割 提取激光直线提取出的直线最小长度
LS Seed Line Points For LaserLine ~-~ 激光分割 提取激光直线种子线段包含的激光数
LS Min Line Points For Laser Line ~-~ 激光分割 提取激光直线提取出的直线包含的最小激光点个数
LS Test Laser Line Flag ~-~ 激光分割 是否开启直线提取测试功能(自测用)
LS PCD File Directory ~-~ 激光分割 PCD文件路径
RecoFile not exist!!!! ~-~ 识别文件不存在
Cannot find shelf, maybe not get left and right rssi data, please check saved pics!!!! ~-~ 无法识别料架腿，打开保存图片以查看激光数据!!!
Cannot find segment, maybe charger pose is too far, please check charger pose!!!! ~-~ 找不到分割线，可能充电桩太远，请查看充电桩位姿!!!!
not find shelf, get some rssi data, but not fit setting, please check setting paramaters!!!! ~-~ 无法识别料架腿，激光强度与设置不匹配！！！
no shape in this scan, please check saved pics!!!! ~-~ 此次未扫描到形状，请查看图片
two lines in left, two lines in right, but points in line is too less, please check saved pics!!!! ~-~ 左侧两条线，右侧两条线，激光线包含的点太少，请查看图片！！！
two left, one right, but points in line is too less, please check saved pics!!!! ~-~ 左侧两条线，右侧一条线，激光线包含的点太少，请查看图片！！！
two right, one left, but points in line is too less, please check saved pics!!!! ~-~ 左侧一条线，右侧两条线，激光线包含的点太少，请查看图片！！！
one line left, one line right, please check saved pics!!!! ~-~ 左侧一条线，右侧一条线，请查看图片！！！
one line left, one line right, but points in line is too less, please check saved pics!!!! ~-~ 左侧一条线，右侧一条线，激光线包含的点太少,请查看图片！！！
get some shapes, but not fit, please check saved pics!!!! ~-~ 识别到的与配置的不匹配，请查看图片！！！
no shape in this scan, please check saved pics!!!! ~-~ 此次未识别到形状，请查看图片！！！
maybe no leg in laser range, not find legs!!!! ~-~ 激光距离内或许没有货架腿
tag reco file is not use in 3.4.6, please select code reco file ~-~ tag文件在3.4.6已经不支持，请使用code文件
zhiwei gain ~-~ 知微相机增益
UseZWMulitExposure ~-~ 知微相机使用多重曝光
mZWMultiExpoLevel ~-~ 知微多重曝光等级
mZWMultiExpoMode ~-~ 知微多重曝光模式
ZWMultiExpoMin ~-~ 知微最小曝光值
ZWMultiExpoMax ~-~ 知微最大曝光值
zhiwei get data time out (s) ~-~ 知微采集等待时间(s)
zhiwei roi size X ~-~ 知微ROI X
zhiwei roi size Y ~-~ 知微ROI Y
zhiwei roi offset X ~-~ 知微ROI X 偏移
zhiwei roi offset Y ~-~ 知微ROI Y 偏移
zhiwei exposureTime ~-~ 知微曝光时间
zhiwei farest image dist ~-~ 知微最远成像距离
obstacle height which can be detected ~-~ 避障检测地面高度
is use Percip advenced param ~-~ 是否使用图漾高级参数
Percip advenced param ~-~ 图漾高级参数
cannot init DaHeng ~-~ 大恒相机初始化失败
DaHeng emStatus error!!! ~-~ 大恒相机状态错误
DaHeng not capture a img!!!! ~-~ 大恒相机采图失败
3D camera : cannot init Hikang EB435I ~-~ 3D相机 ： 海康EB435I 初始化失败
3D camera : cannot set Hikang EB435I frame ~-~ 3D相机 ： 海康EB435I 设置失败
3D camera : cannot open 2x2 ~-~ 3D相机 ： 海康EB435I 降分辨率失败
3D camera : cannot receive laser data from Hikang EB435I ~-~ 3D相机 ： 海康EB435I 未收到激光数据
3D camera : cannot receive data from Hikang EB435I ~-~ 3D相机 ： 海康EB435I 未采集到数据
cannot init Hik ~-~ 初始化海康相机失败
cannot set auto exposure from Hik ~-~ 海康相机设置自动曝光失败
cannot get data from Hik ~-~ 海康相机获取数据失败
hik : set pixel format not equal to camera pixel format!!! ~-~ 海康相机设置像素格式错误
3D camera : cannot init inuSensor ~-~ 3D相机 : 银牛初始化失败
Failed to start to Inuitive Sensor ~-~ 银牛启用数据流失败
Failed to GetCalibrationData ~-~ 银牛获取标定数据失败
Failed to get Depth Stream ~-~ 银牛获取深度图数据流失败
Failed to init Depth Stream ~-~ 银牛初始化深度图数据流失败
Failed to start Depth Stream ~-~ 银牛启动深度图数据流失败
Failed to register Depth Stream ~-~ 银牛注册深度图数据流失败
Inu camera get data delay . ~-~ 银牛获取数据超时
cannot open Livox!!! ~-~ Livox 打开失败
livox mid-70 get data fail!!! ~-~ Livox mid-70 获取数据失败
3D camera : update date delay ~-~ 3D相机 ： 更新数据延迟
cannot init Livox!!! ~-~ Livox 初始化失败
cannot receive laser data from Livox360, ip:  ~-~ 未收到Livox360数据，ip :
3D camera : orbbec not found match serial number ~-~ 3D相机 ： 奥比相机未发现匹配序列号
3D camera : orbbec disconnect ~-~ 3D 相机 ： 奥比断连
percip found device fault ~-~ 图漾相机发现设备失败
percip open device fault ~-~ 图漾相机打开设备失败
percip connect device fault ~-~ 图漾相机连接设备失败
percip open rgb device fault ~-~ 图漾相机打开RGB相机失败
3D camera : connect realsense fault .!!! ~-~ 3D相机 ： realsense 连接失败
3D camera : realsense get data fault .!!! ~-~ 3D相机 ： realsense获取数据失败
3D camera : sick_visionary_t_mini data stream open failed . ~-~ 3D相机 ： sick 打开数据流失败
3D camera : sick_visionary_t_mini visionaryControl open failed . ~-~ 3D相机 ： sick 打开设备失败
3D camera : cannot login sick_visionary_t_mini ~-~ 3D相机 ： sick 登录失败
3D camera : sick_visionary_t_mini Failed to set enDepthMask to true ~-~ 3D相机 ： sick 设置失败
3D camera : sick_visionary_t_mini Failed to logout ~-~ 3D相机 ： sick 退出失败
3D camera : cannot receive laser data from sick_visionary_t_mini ~-~ 3D相机 ： sick 获取数据流失败
cannot init usb-camera with: ~-~ usd相机初始化失败
cannot get usb-camera data: ~-~ usb相机获取数据失败
3D camera : cannot init VZense  ~-~ 3D相机 ： 维感相机初始化失败
3D camera : cannot open VZense  ~-~ 3D相机 ： 维感相机初始化失败
3D camera : set software trigger fault ~-~ 3D相机 ： 软触发设置失败
3D camera : set auto mode fault ~-~ 3D相机 ： 自动模式设置失败
3D camera : cannot receive pointcloud data from Vzense Camera ~-~  3D相机 ： 未收到维感相机点云数据
3D camera : not find zhiwei sensor!!! ~-~  3D相机 ： 未发现知微相机
3D camera : not get zhiwei sensor data!!!, capturePoint is :  ~-~  3D相机 ： 未收到知微相机数据
3D camera : not init zhiwei sensor!!! ~-~ 3D相机 ： 知微相机初始化失败
back laser install pitch ~-~ 叉车货叉下的后视激光雷达安装的俯仰角
back laser install z based on Fork ~-~ 叉车货叉下后视激光雷达相对于货叉的 z 方向偏移量
vmstat log frequency(unit: s) ~-~ vmstat日志频率(单位：秒)
iomonitor log frequency(unit: ms) ~-~ iomonitor日志频率(单位：毫秒)
_iomonitor_read_warn_threshold(unit: kB/s) ~-~ _iomonitor读取警告阈值(单位：千字节/秒)
_iomonitor_write_warn_threshold(unit: kB/s) ~-~ _iomonitor写入警告阈值(单位：千字节/秒)
_iomonitor_read_err_threshold(unit: kB/s) ~-~ _iomonitor读取错误阈值(单位：千字节/秒)
_iomonitor_write_err_threshold(unit: kB/s) ~-~ _iomonitor写入错误阈值(单位：千字节/秒)
Peripheral user data max count ~-~ 外围用户数据最大计数
SeerRoller error: ~-~ SeerRoller错误:
SeerJack error: ~-~ SeerJack错误:
SeerHook error: ~-~ SeerHook错误:
sound play count is invalid: ~-~ 声音播放计数无效：
sound file does not exist: ~-~ 声音文件不存在：
sound file does not exist, sound file read failed: ~-~ 声音文件不存在，声音文件读取失败：
Lift motor name ~-~ 升降电机名称
Lift sensor name ~-~ 升降传感器名称
Highest position of lift ~-~ 升降最高位置
Lowest position of lift ~-~ 升降最低位置
Chassis motor name ~-~ 底盘电机名称
Chassis lift sensor name ~-~ 底盘升降传感器名称
x speed ratio switching distance ~-~ x速度比例切换距离
x speed ratio ~-~ x速度比例
y speed ratio switching distance ~-~ y速度比例切换距离
y speed ratio ~-~ y速度比例
y direction motor speed inverse ~-~ y方向电机速度反转
Lift reach distance ~-~ 升降到达距离
poweroffDO parameters ~-~ 关机数字输出参数
When a dynamic obstacle is in this area, the corresponding DO state is triggered. ~-~ 当动态障碍物在此区域内时，将触发相应的数字输出状态。
Minimum value in the x-direction of the detection area ~-~ 检测区域x方向的最小值
Minimum value in the y-direction of the detection area ~-~ 检测区域y方向的最小值
Maximum value in the x-direction of the detection area ~-~ 检测区域x方向的最大值
Maximum value in the y-direction of the detection area ~-~ 检测区域y方向的最大值
Id of the opened DO, -1 means not enabled ~-~ 打开的数字输出的ID,-1表示未启用
back laser install pitch ~-~ 后置激光安装俯仰
back laser install z based on Fork ~-~ 基于差齿的后置激光z轴安装位置
Cargo containers ~-~ 货物容器
Slip detection window width (ms) ~-~ 打滑检测窗口宽度（毫秒）
No bind ~-~ 不绑定
Release lock ~-~ 释放控制权
Confirm location ~-~ 确认定位
Go to init point ~-~ 导航到初始站点
Go to next point ~-~ 导航到下一个站点
Go to previous point ~-~ 导航到上一个站点
Cancel navigation ~-~ 取消导航
Get lock ~-~ 获取控制权
Set DI ~-~ 设置虚拟DI
Pause or continue navigation ~-~ 暂停/继续导航
The max time threshold for charge DO close. ~-~ 充电DO关闭的最大时间阈值
 Maximum filter number in Do Region ~-~ Do区域中的最大过滤器数量。
modbus DO region group id ~-~ modbus DO区域群组ID。
movable laser id ~-~ 可移动激光器ID。
Turn on ultrasonic DI height detection ~-~ 打开超声波DI高度检测。
Kp ~-~ 比例增益。
Ki ~-~ 积分增益。
observer Filter K ~-~ 观察者滤波器K。
time window for Ki ~-~ Ki的时间窗。
0: Based on LQR Mode, 1: diff pid method ~-~ 0：基于LQR模式，1：差分PID方法。
Jerk during deceleration when unloaded(m/s^3) ~-~ 空载减速时的加加速度（m/s^3）。
Starting acceleration when unloaded ~-~ 空载启动加速度。
Jerk during acceleration when unloaded(m/s^3) ~-~ 空载加速时的加加速度（m/s^3）。
Starting maintenance time when unloaded ~-~ 空载启动保养时间。
Starting acceleration when loaded ~-~ 装载时的启动加速度。
Jerk during acceleration(m/s^3) when loaded ~-~ 装载时加速过程中的加加速度（m/s^3）。
Starting maintenance time when loaded ~-~ 装载时的启动维持时间。
Speed interpolation enabled ~-~ 启用速度插值。
Kalman filtering enabled ~-~ 卡尔曼滤波启用
DepthCamera Collision Points Threshold Number ~-~ 深度相机碰撞点阈值数量
ThetaKd value of line patrol PID ~-~ 巡线PID的ThetaKd值
Whether focre enable obstacle stop distance in Free navigation ~-~ 自由导航中是否强制启用障碍物停止距离
Away obstacle distance in Free navigation ~-~ 自由导航中的避障距离
Free navigation path replan curvature threshold(m-1) ~-~ 自由导航路径重新规划曲率阈值
Free navigation path replan obstacle distance threshold ~-~ 自由导航路径重新规划障碍物距离阈值
Free navigation path replan time threshold(ms) ~-~ 自由导航路径重新规划时间阈值(ms)
Whether or not the maximum speed limit is enabled on the CE vehicle ~-~ CE车辆是否启用最大速度限制
The maximum speed of the CE vehicle(m/s) ~-~ CE车辆的最大速度(m/s)
EtherCAT motor timeout ~-~ EtherCAT电机超时
EtherCAT motor new speed timeout ~-~ EtherCAT电机新速度超时
User error code is 53900~53999 User warning code is 55900~55999 ~-~ 用户错误代码为53900~53999 用户警告代码为55900~55999
Cannot receive frame for a few time ~-~ 一段时间内无法接收帧
Cannot receive MoveFactory instruction for a few time ~-~ 一段时间内无法接收MoveFactory指令
Check EtherCAT bus or the power of motor servo ~-~ 检查EtherCAT总线或电机伺服的电源
Contact SEER ~-~ 联系SEER
Bi-steer offset difference calibration movement started ~-~ 双舵轮舵角偏差差异标定运动开始
Bi-steer offset difference calibration section finished ~-~ 双舵轮舵角偏差差异标定部分运动完成
Unexpected state in bi-steer offset difference calibration movement ~-~ 双舵轮舵角偏差差异标定中出现意外状态
Bi-steer offset difference calibration results generated ~-~ 双舵轮舵角偏差差异标定结果生成
Clear .cp values for bisteer vehicle's steer angle offsets ~-~ 清除双舵轮车舵角偏置值
Bi-steer mean steer offset calibration movement started ~-~ 双舵轮平均舵角标定运动开始
Wait too long for the input data ~~-~ 等待输入数据的时间太长
FAILED to parse the input data ~~-~ 无法解析输入数据
Bi-steer mean offset calibration section finished ~~-~ 双舵轮平均舵角标定部分运动完成
Unexpected state in mean steer offset calibration ~~-~ 在双舵轮平均舵角标定中出现意外状态
FAILED to parse the string in vecManualDataStr ~~-~ 无法解析 vecManualDataStr 中的字符串
The input lateral offset is larger than the measured displacement ~~-~ 输入的侧向偏移大于测量的位移
FAILED to generate results ~~-~ 生成结果失败
The deflection angle of the vehicle when moving forward is ~~-~ 车辆向前移动时的偏转角是
Bi-steer mean offset calibration results generated ~~-~ 生成了双舵轮平均舵角标定结果
The designated laser is found in the model file ~~-~ 指定的激光在模型文件中被找到
The designated laser is NOT found in the model file ~~-~ 指定的激光在模型文件中没有被找到
 ABORTED because the designated laser is NOT found in the model file ~~-~ 因为指定的激光在模型文件中没有被找到而中断
 ABORTED because MCLoc didn't find the designated laser ~~-~ 因为 MCLoc 没有找到指定的激光而中断
Failed to generate results! ~~-~ 生成结果失败！
Clear the .cp values for walk motors ~~-~ 清除步行电机的 .cp 值
Clear the .cp values for steer motors ~~-~ 清除转向电机的 .cp 值
Create virtual devices in model file ~~-~ 在模型文件中创建虚拟设备
Unexpected CalibMoveType ~~-~ 出现意外的标定类型
Update params because .cp file changed ~~-~ 更新参数因为 .cp 文件改变了
Update params because model file changed ~~-~ 更新参数因为模型文件改变了
Wait for MoveTask to start running for too long ~-~ 等待MoveTask开始运行时间过长
 ABORTED because MoveFactory didn't answer in time ~-~ 因MoveFactory未及时应答而中止
Wait for MoveTask to finish for too long ~-~ 等待MoveTask完成时间过长
 ABORTED because MoveFactory didn't finish in time ~-~ 因MoveFactory未及时完成而中止
Wait for relocation to finish for too long ~-~ 等待重新定位完成时间过长
 ABORTED because relocation didn't finish in time ~-~ 因重新定位未及时完成而中止
Wait for IMU calibration to finish for too long ~-~ 等待IMU校准完成时间过长
 ABORTED because IMU calibration didn't finish in time ~-~ 因IMU校准未及时完成而中止
Current calibration task FINISHED ~-~ 当前标定任务完成
All calibration tasks FINISHED ~-~ 所有标定任务完成
Current calibration task ABORTED ~-~ 当前标定任务中止
All calibration tasks ABORTED ~-~ 所有标定任务中止
Initialization generate INVALID parameters for theta-shaped movement ~-~ 初始化生成θ型运动的参数无效
Rotating 90° ~-~ 旋转90°
Theta-shaped movement section finished ~-~ θ型运动部分完成
Moving in clockwise arc ~-~ 沿顺时针方向移动弧形
Rotating -90° ~-~ 旋转-90°
Moving forward ~-~ 向前移动
Moving in counterclockwise arc ~-~ 沿逆时针方向移动弧形
Moving backward ~-~ 向后移动
Unexpected state in theta-shaped movement ~-~ θ型运动中出现意外状态
 initialized ~-~ 初始化完成
Start listening for data input ~-~ 开始监听数据输入
 continue ~-~ 继续
Data parsed ~-~ 数据解析完成
Data received ~-~ 数据接收完成
Initialization generate INVALID parameters for d-shaped movement ~-~ 初始化生成D形运动的参数无效
Please confirm the parameters of the d-shaped movement ~-~ 请确认D形运动的参数
Wait too long for the confirmation ~-~ 等待确认时间过长
Parameters of the d-shaped movement confirmed ~-~ D形运动的参数已确认
d-Shaped movement section finished ~-~ D形运动部分完成
Initialization generate INVALID parameters for claw-shaped movement ~-~ 初始化生成爪形运动的无效参数
Going left arc forward ~-~ 向前左转弧形运动
Claw-shaped movement section finished ~-~ 爪形运动部分完成
Going left arc backward ~-~ 向后左转弧形运动
Going straight forward ~-~ 直线向前运动
Going straight backward ~-~ 直线向后运动
Going right arc forward ~-~ 向前右转弧形运动
Going right arc backward ~-~ 向后右转弧形运动
Rotating counter-clockwise ~-~ 逆时针旋转
Claw movement finished ~-~ 爪形运动结束
Rotating clockwise ~-~ 顺时针旋转
Unexpected state ~-~ 意外状态
Load single steer offset file ~-~ 载入单舵轮舵角补偿文件
Update single steer offset file ~-~ 更新单舵轮舵角补偿文件
CANNOT initialize current calibration type ~-~ 无法初始化当前的校准类型
CANNOT call _Record function for current calibration type ~-~ 无法为当前标定类型调用_Record函数
CANNOT call _GenResults function for current calibration type ~-~ 无法为当前标定类型调用_GenResults函数
ABORTED because MoveFactory didn't respond properly ~-~ 已中止，因为MoveFactory没有正确响应
INVALID calculation result for trajectory fitting error estimation ~-~ 轨迹拟合误差评估的计算结果无效
clearCalibAll ~-~ 清除所有标定结果
Save the calibration results after clearCalib ~-~ 清除标定结果后保存
FAILED to parse calibJsonStr passed to CalibrationTask::clearCalib ~-~ 在清除标定文件中解析错误
cancelCalib ~-~ 取消标定
 ABORTED as requested ~-~ 因请求终止
saveCalibResult ~-~ 保存标定结果
clearCalibResult ~-~ 清除标定结果
FAILED to parse calibJsonStr passed to CalibrationTask::setCalibTask ~-~  在设置标定文件中解析错误
CalibrationTask::setCalibTask REJECTED new calibration task(s) as there is a task under execution ~-~ 因正在执行而中断
The designated locCamera is found in the model file ~-~ 指定的locCamera在模型文件中被找到了
The designated locCamera is NOT found in the model file ~-~ 指定的locCamera在模型文件中没有找到
 ABORTED because the designated locCamera is NOT found in the model file ~-~ 已中止，因为指定的locCamera在模型文件中没有找到
locCamera calibration movement started ~-~ locCamera标定运动开始
locCamera calibration section finished ~-~ locCamera标定部分完成
Unexpected state in locCamera calibration movement ~-~ 在locCamera标定运动中出现意外状态
locCamera calibration results generated ~-~ locCamera标定结果已生成
The designated RealSense camera is found in the model file ~-~ 指定的RealSense摄像头在模型文件中被找到了
The designated RealSense camera is NOT found in the model file ~-~ 指定的RealSense摄像头在模型文件中没有找到
 ABORTED because the designated RealSense camera is NOT found in the model file ~-~ 已中止，因为指定的RealSense摄像头在模型文件中没有找到
FAILED to parse the input data in vecManualDataStr ~-~ 解析vecManualDataStr中的输入数据失败
 ABORTED because too few data group aquired ~-~ 已中止，因为获得的数据组太少
RealSense camera calibration results generated ~-~ RealSense摄像头校准结果已生成
 ABORTED because the designated camera is NOT found in the model file ~-~ 已中止，因为指定的摄像头在模型文件中没有找到
 ABORTED because the service returned invalid result ~-~ 已中止，因为服务返回了无效结果
IRCam calibration results generated ~-~ IRCam校准结果已生成
The designated camera is found in the model file ~-~ 指定的摄像头在模型文件中被找到了
The designated camera is NOT found in the model file ~-~ 指定的摄像头在模型文件中没有找到
The designated camera is NOT found in the model file, NO .cp value changed! ~-~ 指定的摄像头在模型文件中没有找到，没有.cp值改变！
The designated camera is NOT mounted on arm ~-~ 指定的摄像头在机械臂上没有找到
 ABORTED because the designated camera is NOT eligible for hand-eye caliration ~-~ 中止，因为指定的摄像头不适用于手眼校准
JSON data contains LESS groups than required ~-~ JSON数据包含的组少于所需
armData is incomplete ~-~ 机械臂数据不完整
INVALID cameraData sent to calibration plugin ~-~ 发送到校准插件的摄像头数据无效
cameraData is incomplete ~-~ 摄像头数据不完整
JSON data contains incomplete group ~-~ JSON数据包含不完整的组
JSON data received is NOT array with elements ~-~ 收到的JSON数据不是带有元素的数组
Hand-eye calibration results generated ~-~ 已生成手眼校准结果
The designated charger is found in the model file ~-~ 指定的充电器在模型文件中找到
The designated charger is NOT found in the model file ~-~ 指定的充电器在模型文件中未找到
No input data received! ~-~ 未接收到输入数据！
Some requested data is missing in the input JSON ~-~ 输入的JSON中缺少一些请求的数据
There is no data in the input JSON ~-~ 输入的JSON中没有数据
FAILED to parse the string in vecManualDataStr ~-~ 解析vecManualDataStr中的字符串失败
The designated force sensor is found in the model file ~-~ 指定的力传感器在模型文件中找到
The designated force sensor is NOT found in the model file ~-~ 指定的力传感器在模型文件中未找到
 ABORTED because the designated force sensor is NOT found in the model file ~-~ 中止，因为模型文件中未找到指定的力传感器
FAILED to parse the input data in vecManualDataStr ~-~ 解析vecManualDataStr中的输入数据失败
JSON data contains LESS groups than required ~-~ JSON数据包含的组少于所需
armData is incomplete ~-~ 机械臂数据不完整
forceData is incomplete ~-~ 力数据不完整
JSON data contains incomplete group ~-~ JSON数据包含不完整的组
JSON data received is NOT array with elements ~-~ 收到的JSON不是数组
 ABORTED because of incomplete data ~-~ 因不完整数据终止
 ABORTED because too few data group aquired ~-~ 因过少的组终止
Force Sensor Zero calibration results generated ~-~ 生成了力传感器零点校准结果
The designated force sensor is NOT found in the model file, NO .cp value changed! ~-~ 指定的力传感器在模型文件中未找到，没有改变.cp值！
The designated linear motor is NOT found in the model file ~-~ 指定的直线电机在模型文件中未找到
 ABORTED because the designated linear motor is NOT found in the model file ~-~ 已中止，因为未在模型文件中找到指定的直线电机
Fork test movement started ~-~ 叉车测试移动开始
Fork going to zero ~-~ 叉车归零
Fork test move section finished ~-~ 叉车测试移动部分完成
Moving fork to start height ~-~ 叉车移动到起始高度
Reached start height, hold for a second ~-~ 达到起始高度，保持一秒
Holding ended, starting acceleration ~-~ 保持结束，开始加速
Holding ended, starting constant speed motion ~-~ 保持结束，开始匀速运动
Start fork constant speed movement ~-~ 开始叉车匀速移动
Deceleration ended, hold for a second ~-~ 减速结束，保持一秒
 DONE because fork reached max height allowed by parameters ~-~ 完成，因为叉车达到了参数允许的最大高度
Starting deceleration ~-~ 开始减速
Fork test move data and plots saved ~-~ 叉车测试移动数据和图表已保存
The designated Camera is found in the model file ~-~ 指定的摄像头在模型文件中已找到
The designer Camera is NOT found in the model file ~-~ 指定的摄像头在模型文件中未找到
 ABORTED because the designated Camera is NOT found in the model file ~-~ 已中止，因为在模型文件中未找到指定的摄像头
FAILED to parsed ~-~ 解析失败
There is no data in the input JSON ~-~ 输入的JSON中没有数据
 ABORTED because the service returned invalid result ~-~ 已中止，因为服务返回了无效结果
GNSS calibration results generated ~-~ 生成了GNSS校准结果
External parameters of the GNSS device:  ~-~ GNSS 设备的外部参数：
The designated IMU is found in the model file ~-~ 指定的 IMU 在模型文件中找到
The designated IMU is NOT found in the model file ~-~ 指定的 IMU 在模型文件中未找到
 ABORTED because the designated IMU is NOT found in the model file ~-~ 因为模型文件中未找到指定的 IMU 而中止
IMU initial calibration movement started ~-~ IMU 初始校准运动开始
IMU initial calibration section finished ~-~ IMU 初始校准部分完成
No valid data is recorded during the calibration ~-~ 在校准过程中没有记录有效数据
 ABORTED because NO valid data is recorded during the calibration ~-~ 因为在校准过程中没有记录有效数据而中止
FAILED to generate data matrices for IMUInitCalibrator ~-~ 未能为 IMUInitCalibrator 生成数据矩阵
 ABORTED because it FAILED to generate data matrices for IMUInitCalibrator ~-~ 因为未能为 IMUInitCalibrator 生成数据矩阵而中止
FAILED to generate data matrices for IMUAttitudeIdentifier ~-~ 未能为 IMUAttitudeIdentifier 生成数据矩阵
 ABORTED because it FAILED to generate data matrices for IMUAttitudeIdentifier ~-~ 因为未能为 IMUAttitudeIdentifier 生成数据矩阵而中止
 ABORTED because the given side length of the calibration space is NOT enough ~-~ 因为提供的校准空间边长不足而中止
The designated GNSS is found in the model file ~-~ 指定的 GNSS 在模型文件中找到
The designated GNSS is NOT found in the model file ~-~ 指定的 GNSS 在模型文件中未找到
 ABORTED because the designated GNSS is NOT found in the model file ~-~ 因为模型文件中未找到指定的 GNSS 而中止
The designated laser is found in the model file ~-~ 指定的激光器在模型文件中找到
The designated laser is NOT found in the model file ~-~ 指定的激光器在模型文件中未找到
 ABORTED because the designated laser is NOT found in the model file ~-~ 因为模型文件中未找到指定的激光器而中止
 ABORTED because MCLoc didn't find the designated laser ~-~ 因为MCLoc 未找到而中止
GNSS-Odom calibration movement started ~-~ GNSS-Odom标定运动开始
IRCam-Odom calibration movement started ~-~ IRCam-Odom标定运动开始
GenenalCam-Odom calibration movement started ~-~ GenenalCam-Odom标定运动开始
Laser-odom calibration movement started ~-~ 激光-里程计标定运动开始
Camera-odom calibration section finished ~-~ 摄像头-里程计标定部分完成
Laser-odom calibration section finished ~-~ 激光-里程计标定部分完成
Unexpected state in laser-odom calibration movement ~-~ 激光-里程计标定运动中出现意外状态
The identification FAILED to return valid values ~-~ 识别未能返回有效值
 ABORTED because parameter identification FAILED ~-~ 由于参数识别失败，操作被终止
camera-odom calibration results generated ~-~ 摄像头-里程计标定结果生成
Laser-odom calibration results generated ~-~ 激光-里程计标定结果生成
NO results for y positions of walk motors are generated ~-~ 行走电机的y位置没有产生结果
Clear the .cp values for walk motors ~-~ 清除行走电机的.cp值
Clear the .cp values for walk and steer motors ~-~ 清除行走和转向电机的.cp值
Laser calibration based on odometer results generated ~-~ 基于里程计结果的激光校准生成
The designer laser is NOT found in the model file ~-~ 在模型文件中找不到设计好的激光器
FAILED to callService in ObsLaserCalibRecord ~-~ 调用ObsLaserCalibRecord中的callService失败
JSON data don't match to required ~-~ JSON数据不符合要求
JSON data received is NOT array with elements ~-~ 接收到的JSON数据不是带有元素的数组
FAILED to parse data in ObsLaserCalibRecord ~-~ 解析ObsLaserCalibRecord中的数据失败
Omnidirectional movement started ~-~ 全方位移动开始
Omni move section finished ~-~ 全方位移动部分完成
Unexpected state in omni movement ~-~ 全方位移动中出现意外状态
Roller angle calibration results generated ~-~ 滚轮角度标定结果生成
Clear .cp value for rollAngle of omni vehicle ~-~ 清除全向车辆rollAngle的.cp值
The designated laser is NOT found in the model file ~-~ 指定的激光器在模型文件中未找到
The designated laser is found in the model file ~-~ 指定的激光器在模型文件中找到了
The caliration process FAILED because NOT ALL quadrant have wheels ~-~ 因为不是所有象限都有轮子，校准过程失败
The caliration process FAILED to collect data of right number of wheel ~-~ 校准过程未能收集到正确数量的轮子数据
The caliration process FAILED to collect enough data ~-~ 校准过程未能收集到足够的数据
The caliration process FAILED because data records of different wheels are NOT of the same size ~-~ 因为不同轮子的数据记录大小不一，校准过程失败
Failed to generate results! ~-~ 生成结果失败！
Clear the .cp values for walk motors ~-~ 清除步行电机的.cp值
Hybrid omni move start omni move ~-~ 混合全向移动开始全向移动
Hybrid omni move FINISHED ~-~ 混合全向移动完成
The designated optical_motion_capture is found in the model file ~-~ 指定的光学运动捕捉在模型文件中找到了
The designated optical_motion_capture is NOT found in the model file ~-~ 指定的光学运动捕捉在模型文件中未找到
The identification FAILED to return valid values ~-~ 识别失败，未返回有效值
Optical-odometer calibration results generated ~-~ 生成了光学里程计校准结果
NO results for y positions of walk motors are generated ~-~ 未生成步行电机y位置的结果
Clear the .cp values for walk motors ~-~ 清除步行电机的.cp值
The designated PGV is found in the model file ~-~ 指定的PGV在模型文件中找到了
The designated PGV is NOT found in the model file ~-~ 指定的PGV在模型文件中未找到
ABORTED because the designated PGV is NOT found in the model file ~-~ 因为未在模型文件中找到指定的PGV而中止
PGV calibration movement started ~-~ PGV标定运动开始
Trial movement started for PGV calibration ~-~ PGV标定试探运动开始
PGV calibration section finished ~-~ PGV标定部分完成
Vehicle will rot around its own center ~-~ 车辆将围绕自己的中心旋转
 movement started for PGV calibration ~-~ 开始进行PGV标定移动
Unexpected state in PGV calibration movement ~-~ PGV标定移动中出现意外状态
No valid data is recorded during the calibration ~-~ 标定期间未记录有效数据
 ABORTED because NO valid data is recorded during the calibration ~-~ 由于标定期间未记录有效数据而中止
PGV-odom calibration movement started ~-~ PGV-里程计标定移动开始
Trial forward move started ~-~ 试验向前移动开始
PGV-odom calibration section finished ~-~ PGV-里程计标定部分完成
Trial backward move started ~-~ 试探向后移动开始
GoPGV movement started for PGV-odometer calibration ~-~ 开始GoPGV移动以进行PGV-里程计标定
Unexpected state after GoPGV movement ~-~ 在GoPGV移动后出现意外状态
The calibration process FAILED to collect enough data for identification ~-~ 标定过程未能收集足够的数据进行识别
PGV-odometer calibration results generated ~-~ 生成PGV-里程计标定结果
Clear the .cp values for walk motors ~-~ 清除步进电机的.cp值
Some requested data is missing in the input JSON ~-~ 输入的JSON中缺少一些请求的数据
There is no data in the input JSON ~-~ 输入的JSON中没有数据
FAILED to parsed ~-~ 无法解析
can not find CalibrationTask plugin ~-~ 找不到CalibrationTask插件
Can not find steerOffsetFile ~-~ 找不到steerOffsetFile
Data not enough ~-~ 数据不足
Pass ~-~ 通过
No pass, please continue ~-~ 未通过，请继续
Go straight ~-~ 直行
Movement section finished ~-~ 移动部分结束
Steering to 0° ~-~ 转向至0°
Unexpected state ~-~ 非预期状态
Rotating ~-~ 旋转中
Steering ~-~ 转向中
FAILED ~-~ 失败
Steered ~-~ 已转向
Rotated ~-~ 已旋转
No input data received! ~-~ 未接收到输入数据！
Update steerOffsetFile ~-~ 更新转向偏移文件
The designated laser is found in the model file ~-~ 指定的激光器在模型文件中被找到
The designer laser is NOT found in the model file ~-~ 设计指定的激光器在模型文件中未找到
 ABORTED because the designated laser is NOT found in the model file ~-~ 因未在模型文件中找到指定的激光器而中止
Data is not enough ~-~ 数据不足
section finished ~-~ 部分结束
 ABORTED because MCLoc didn't find the designated laser ~-~ 因MCLoc未找到指定的激光器而中止
Failed ~-~ 失败
Steering to 90° ~-~ 转向至90°
Steering to -90° ~-~ 转向至-90°
Rotating ~-~ 旋转
Clear .cp value of steer vehicle ~-~ 清除转向车辆的.cp值
The designated laser is found in the model file ~-~ 指定的激光器在模型文件中找到
The designated laser is NOT found in the model file ~-~ 指定的激光器在模型文件中未找到
 ABORTED because the designated laser is NOT found in the model file ~-~ 中止，因为模型文件中未找到指定的激光器
SteerCalibMinSpeed NOT lower than SteerCalibMaxSpeed ~-~ 校准最小速度不低于校准最大速度
 ABORTED because SteerCalibMinSpeed NOT lower than SteerCalibMaxSpeed ~-~ 中止，因为校准最小速度不低于校准最大速度
Number of wheel speed samples is ZERO ~-~ 轮速样本数为零
 ABORTED because the wheel speed sample setting is INAPPROPRIATE ~-~ 中止，因为轮速样本设置不当
Number of steer angle samples is ZERO as the steer range is TOO SMALL ~-~ 转向角样本数为零，因为转向范围太小
 ABORTED because the steer range is TOO SMALL ~-~ 中止，因为转向范围太小
Steer vehicle piecewise laser-odometer calibration started ~-~ 分段激光测距校正已开始
Steer vehicle piecewise laser-odometer calibration section finished ~-~ 分段激光测距校正已完成
No valid data section start is recorded ~-~ 未记录有效数据段的开始
No valid data section end is recorded ~-~ 未记录有效数据段的结束
Data section is too short to be counted ~-~ 数据段太短，无法计数
Data section recorded ~-~ 数据段已记录
 FAILED to generate results because valid sample count is NOT enough to form a grid ~-~ 因为有效样本数量不足以形成网格而失败
ALL wheel speed samples have been successfully collected! ~-~ 所有轮速样本已成功收集！
Clear the .cp values for walk and steer motors ~-~ 清除行走和转向电机的.cp值
 ABORTED because the given side length of the calibration space is NOT enough ~-~ 中止，因为标定空间的给定边长不足
 ABORTED because MCLoc didn't find the designated laser ~-~ 中止，因为MCLoc没有找到指定的激光器
Laser-odom calibration movement started ~-~ 激光-里程计标定运动开始
Camera-odom calibration section finished ~-~ 相机-里程计标定运动结束
Laser-odom calibration section finished ~-~ 激光-里程计标定运动结束
Unexpected state in laser-odom calibration movement ~-~ 激光测距-里程计校准运动中出现意外状态
The designated steer motor is NOT found in the model file ~-~ 模型文件中未找到指定的转向电机
 ABORTED because the designated steer motor is NOT found in the model file ~-~ 中止，因为模型文件中未找到指定的转向电机
Steer angle range calibration movement started ~-~ 转向角度范围校准运动开始
Movement started ~-~ 运动开始
section finished ~-~ 部分完成
Unexpected state ~-~ 意外状态
calibration results generated ~-~ 校准结果已生成
Clear .cp value for steer motor steer offset ~-~ 清除转向电机转向偏移的.cp值
Test started ~-~ 测试开始
The input lateral offset is larger than the measured displacement  ~-~ 输入的横向偏置大于其测量值
The defletion angle of the vehicle when moving forward is  ~-~ 车辆向前行驶时的偏转角度
 ABORTED because MoveFactory didn't respond properly ~-~ 因 MoveFactory 未正确响应终止
 ABORTED because the designated PGV is NOT found in the model file ~-~ 因 PGV 未找到终止
The caliration process FAILED to collect enough data for identification ~-~ 因未收集到足够辨识数据标定失败
differential drive ~-~ 差动驱动
steer drived by diff ~-~ 差速转向
Steer Kp ~-~ 转向比例系数
steer Kd ~-~ 转向微分系数
action success. ~-~ 机械臂动作执行成功
inverse kinematics error. ~-~ 机械臂逆解错误
normal error. ~-~ 机械臂一般性错误（UR机械臂模式错误，无法进行当前操作）
task stop botton on. ~-~ 任务链取消按钮按下
json data error. ~-~ 任务链json格式错误
can not find recognition result. ~-~ 没有识别结果
fail load user coordinary. ~-~ 用户坐标系加载失败
velocity or accelerate error. ~-~ 机械臂运动速度/加速度异常
fail identify marker. ~-~ Marker识别失败
gripper control error. ~-~  夹爪控制异常
safe check error. ~-~ 任务执行前安全位置检查异常
arm disconnected. ~-~ 机械臂断开连接
arm payload set error. ~-~ 机械臂负载设置报错
binTask error: {1} ~-~ 机械臂执行任务链报错：{1}后面是具体的错误类型
default move joint velocity [0, 1] ~-~ 机械臂关节运动默认全局速度
default move joint acceleration [0, 1] ~-~ 机械臂关节运动默认全局加速度
default move line end velocity [0, 1] ~-~ 机械臂直线运动默认全局速度
default move line end acceleration [0, 1] ~-~ 机械臂直线运动默认全局加速度
AUBO-i5 receive frequency ~-~ aubo-i5机械臂接收数据频率
AUBO-i5 ip ~-~ 机械臂ip
AUBO-i5 port ~-~ 机械臂端口
JAKA-Zu receive frequency ~-~ 机械臂接收数据频率
JAKA-Zu ip ~-~ 机械臂ip
JAKA-Zu port ~-~ 机械臂端口
Dobot-Cr receive frequency ~-~ 机械臂接收数据频率
Dobot-Cr ip ~-~ 机械臂ip
Dobot-Cr port ~-~ 机械臂端口
hitbot scara generation ~-~ hitbot scara机械臂硬件版本
hitbot scara z_travel ~-~ hitbot 机械臂Z轴行程
Save Joint1's orientation ~-~ 安全点位关节1的角度（red）
Save Joint2's orientation ~-~ 安全点位关节2的角度（red）
Save Joint3's orientation ~-~ 安全点位关节3的角度（red）
Save Joint4's orientation ~-~ 安全点位关节4的角度（red）
Save Joint5's orientation ~-~ 安全点位关节5的角度（red）
Save Joint6's orientation ~-~ 安全点位关节6的角度（red）
End Devices from 800 ~-~ 末端夹爪由末端800控制器控制
End Devices from 2000 ~-~ 末端夹爪由2000控制器控制
Scanner from 800 ~-~ 扫码由末端800控制器控制
Scanner from 2000 ~-~ 扫码由2000控制器控制
Scanner code from Cognex ~-~ 使用康耐视智能相机扫码
UR arm move joint stop acc ~-~ UR机械臂关节运动停止加速度
UR arm move line stop acc ~-~ UR机械臂直线运动停止加速度
Current Model is DW8 ~-~ 当前机械臂是DW8模式
Current Model is AuboCompound ~-~ 当前机械臂是Aubo模式
arm ip ~-~ 机械臂IP
modbus port ~-~ modbus通信端口
slave id ~-~ modbus通信从站id
coils number ~-~ 线圈数
error msg when this register is equal to setting value ~-~ 寄存器与设置值相同时的错误信息
true value of coils represent error ~-~  coils值为true时代表报错
Discrete Inputs number ~-~ 分离输入数值
true value of Discrete Inputs represent error ~-~ 输入值为true时代表报错
Holding Registers number ~-~ 保持寄存器值
expected read value ~-~ 读数据异常值
Input Registers number ~-~ 输入寄存器的值
error code ~-~ 错误码
ArmAdapter : no arm connected. ~-~ 机械臂未连接
arm info publish wait time (ms) ~-~ 机械臂发布数据的频率
scara jog move offset (mm) ~-~ scara机械臂点动偏移量
Scara Rotation Min Vaule (degree) ~-~ scara机械臂末端转动角度最小值
Scara Rotation Max Vaule (degree) ~-~ scara机械臂末端转动角度最大值
gripper check error ~-~ 夹爪量程检查的误差范围
device status check fail. ~-~ 复合机机器人设备状态检查失败，包括机械臂、夹爪、相机、力控等设备的状态
Cannot Use Two Type At Same Time!Please Cancel One ~-~ 不能给机械臂同时勾选两种模式
Cannot MoveJog With Pause Status!Please Cancel Or Continue ~-~ 机械臂运动暂停状态下无法点动控制机械臂
Please Choose The ModelType Before Use Auto-Calibration! ~-~ 机械臂自动手眼标定需要选择一种机械臂运动模式
Json Data Type Error Because Speed: {1} is out of the Range [{2}, {3}] ~-~ JSON数据错误：机械臂速度{1}不在范围[{2}, {3}]内
Json Data Type Error Without UserFrame's value!Please Check it ~-~ JSON数据错误：没有用户坐标系的值
Json Data Type Error Without BinSize's value!Please Check it! ~-~ JSON数据错误：没有容器尺寸
Json Data Type Error Without TargetBinIndex!!Please Check it! ~-~ JSON数据错误：没有目标容器的ID
Json Data Type Error Because TargetIndex:{1} is out of the Range:{2} Please Check it! ~-~ JSON数据错误：目标容器的ID{1}不在范围内{2}
Json Data Error ~-~ JSON 数据错误
Not Support With {1} Points ~-~ 计算用户坐标系时点的个数错误， 只能是3个点
Json Data Value Error Because CP:{1} is out of the Range ( {2}, {3} ] ~-~ JSON数据错误：Aubo机械臂的半径{1}必须在({2}, {3}]范围内
ArmAdapter : Protective Stopped. ~-~ 机械臂保护性停止
ArmAdapter: arm internal error: {1} ~-~ 机械臂内部错误，错误码为{1}
ArmAdapter : Protective Stopped. ~-~ 机械臂保护性停止
ArmAdapter : Emergency Stopped. ~-~ 机械臂紧急停止
ArmAdapter normal error: arm mode is {1}, can not power on ~-~ 机械臂模式状态错误：机械臂模式状态为{1}，此状态不能上电
ArmAdapter normal error: arm mode is {1}, can not power off ~-~ 机械臂模式状态错误：机械臂模式状态为{1}，此状态不能下电
ArmAdapter normal error: arm mode is {1}, can not break release ~-~ 机械臂模式状态错误：机械臂模式状态为{1}，此状态不能释放抱闸
ArmAdapter normal error: arm is disconnected, cannot shut down via RoboShop! ~-~ 机械臂模式状态错误：机械臂模已断链，此状态无法关机
ArmAdapter normal error: arm safety mode is {1}, can not unlock protective stop! ~-~ 机械臂模式状态错误：机械臂安全模式状态为{1}，此状态不能解除保护性停止
ArmUR: Cannot Reupload Script! Please Check the Arm Status ~-~ UR机械臂无法加载脚本
Get Vector Z Error, Not Support With Different Posture! Please Check Point4 and Point5! ~-~ 无法计算Z轴， 点4和点5的姿态不一致
Get Vector X Error, Not Support With Different Posture! Please Check Point4 and Point6! ~-~ 无法计算X轴， 点4和点5的姿态不一致
Cannot Compute With: {1} Points ~-~ 输入的点的个数错误，无法计算用户坐标系
Compute With Three Same Points! ~-~ 输入的是3个相同的点，无法计算
rbk_3dcamera - has not been actived, please contact SEER to active this function ~-~ rbk_3dcamera 功能未激活，请联系SEER激活该功能
is use Percip advenced param,do not modify ~-~ 启用图漾高级参数，不可修改
Percip advenced param,do not modify ~-~ 图漾高级参数，不可修改
cannot set exposure time from Hik ~-~ 海康相机设置曝光时间失败
3D camera : cannot init Lanxin ~-~ 3D 相机 ： 蓝芯初始化失败
3D camera : cannot get device list for Lanxin ~-~ 3D 相机 ： 蓝芯获取相机列表失败
3D camera : cannot found device for Lanxin ~-~ 3D 相机 ： 蓝芯发现设备失败
3D camera : cannot enable depth stream for Lanxin ~-~ 3D 相机 ： 蓝芯启用深度流失败
3D camera : start stream fault for Lanxin ~-~ 3D 相机 ： 蓝芯打开数据流失败
ip already connected,cannot open Livox!!! ~-~ ip 已被连接，Livox打开失败
3D camera : cannot connect sick_visionary_t_mini ~-~ 3D 相机 ： SICK连接失败
3D camera : cannot receive frame from sick_visionary_t_mini ~-~ 3D 相机 ： SICK接受数据失败
3D camera : cannot init Vzense ~-~ 3D 相机 ： 维感初始化失败
3d mark file not exist!!!, please check ~-~ 3d mark 识别文件不存在，请检查
Recognize File Not Exist,Please Check! ~-~ 识别文件不存在，请检查
Recognize File Not Exist ~-~ 识别文件不存在，请检查
Pallet Recognize File Not Exist,Please Check Every Pallet! ~-~ 栈板识别文件不存在，请检查
tag file not exist!!!, please check ~-~
lebel file not exist!!!, please check ~-~
pallet_obs_area file not exist!!!, please check ~-~
not found camera enable [useForHasBinDetect] ~-~
Recognition has removed ground. if you don't want, set HorizontalProjectionDistance little than ~-~
Custom Recognize File Txt ID is null, Please Check ! ~-~
the value must be positive , or the num of point less than 3! ~-~
pallet score ~-~  栈板匹配分数
plane score ~-~ 平面匹配分数
candiateAngle ~-~ 候选角度
pallet segment param ~-~ 栈板分割参数
pallet segment param,If the number of plane points is less than this value, a fine correction is required ~-~
pallet segment param,Clustering ablation distance threshold (unit :m), distances less than this distance will be merged,0 indicates disabled ~-~
Improvements using pallets ~-~
pallet Match Method ~-~ 栈板匹配方法
Horizontal projection distance, used to detect removal of ground points ~-~ 水平投影距离，用来决定是否去除地面
The minimum number of points that is considered an object ~-~
The Scope of Roi's X value ~-~ 跌落检测ROIX值
The Minimum Value of Roi's Y ~-~ 跌落检测最小ROIY值
The Maximum Value of Roi's Y ~-~ 跌落检测最大ROIY值
The Scope of Roi's Z value ~-~ 跌落检测ROIZ值
trigger wait time (s) ~-~ 触发等待时间
threshold of pallet thickness ~-~ 栈板面厚度阈值
threshold of pallet detect ratio ~-~ 栈板检测率阈值
threshold of pallet similarity ~-~ 栈板识别相似度阈值
Multi-pallet recognition method only support CUSTOM_PALLET_TEMPLATE ,POLYGON_TEMPLATE and PALLET_PARAM ~-~
3D measure result has shown there is no Goods on the pallet ~-~ 没有货物在栈板上
3D measure result has shown goods's width exceeds threshold,which is ~-~ 3D 测量结果显示货物的宽度超过了
3D measure result has shown goods's height exceeds threshold,which is ~-~ 3D 测量结果显示货物的高度超过了
3D measure result has shown goods's width and height exceeds threshold,which width is ~-~
no pallet rec_file can be used ~-~ 没有符合要求的栈板识别文件
cannot extract plane from current pointCloud ~-~ 当前拍照找不到栈板平面
score is : ~-~ 匹配分数是
score pallet is : ~-~ 栈板匹配分数是
cannot extract plane from current pointCloud after loop all params ~-~
Network Interface Card temperature notification threshold(°C) ~-~ 网卡温度提醒阈值(°C)
CPU temperature notification threshold(°C) ~-~ CPU 温度提醒阈值(°C)
Temperature:{1} ~-~ 温度:{1}
should be greater than threshold is: ~-~ 应当大于 threshold
!!!please check ~-~ 请检查！
should be greater than scorePallet is ~-~ 应当大于 scorePallet
3D measure result has shown goods's width exceeds threshold,which is {1} ~-~ 3D 测量结果显示货物的宽度超过了{1}
3D measure result has shown goods's height exceeds threshold,which is {1} ~-~ 3D 测量结果显示货物的高度超过了{1}
and height is ~-~ 并且高度是
3D measure result has shown goods's width and height exceeds threshold,which width is {1}  and height is {2} ~-~ 3D 测量结果显示货物的宽度超过了 {1},高度超过了{2}
score is : {1} should be greater than threshold is: {2} !!!please check ~-~ 栈板插孔匹配分数是 {1},应当大于 threshold {2},请检查！
score pallet is :  {1} should be greater than scorePallet is {2} !!!please check ~-~ 栈板匹配分数是{1}，应当大于 scorePallet {2}，请检查！
pocketWidth * 2 + pocketSpacing is : {1}  should be less than palletWidth is: {2} ~-~ 当前识别文件插孔和支柱宽度{1}小于栈板宽度{2}，请检查！
pocketHeight+pocketGroundHeight is :  {1}  should be less than palletHeight is  {2}  !!!please check ~-~ 当前识别文件插孔高度和离地高度{1}小于栈板高度{2}，请检查！
goods exceed the pallet {1} m! ~-~ 货物超出栈板 {1}m
pocketHeight+pocketGroundHeight is : {1}  should be less than palletHeight is  {2} !!!please check ~-~ 当前识别文件插孔高度和离地高度{1}小于栈板高度{2}，请检查！
3D camera : berxel not found match serial number ~-~ 3D 相机 ：未发现匹配的博升相机系列号
3D camera : berxel disconnect . ~-~ 3D 相机 ：博升断链
3D camera : cannot init Berxel ~-~ 3D 相机 ：博升初始化失败
3D camera : cannot get data Berxel ~-~ 3D 相机 ：未收到博升相机数据
Activate the joystick ~-~ 激活手柄
Enable keys ~-~ 使能键
Close the joystick ~-~ 关闭手柄
Forward-Backward-TurnLeft-TurnRight ~-~ 前进-后退-左转-右转
Up/Down for line speed increase/decrease, Right/Left for angular speed increase/decrease ~-~ 上下键调整线性速度，左右键调整角速度
Forward-Backward(Non-Omni)/FullDirection(Omni-Only) ~-~ 前进-后退(非全向车)/全向移动(仅限全向车)
Set speed ~-~ 调整速度
rbk_laser_loc is not actived ~-~ 雷达定位没有激活
No enough 3D pointCloud in current map,please check or not use 3DLocalization with Current Laser ~-~ 当前地图中没有足够的 3D 点云，请检查或不使用当前激光的 3D 定位模式
stop because of low confidence ~-~ 因置信度较低而停止
ReferenceObject area is blocked,id: {1} and real laser num is : {2}, virtual laser Num: {3} ~-~ 参考物体区域被阻挡 id ：{1}，实际激光数量为：{2} 虚拟激光数量：{3}
Detect skid and stop AGV ~-~ 检测打滑并停止 AGV 模式
The tag:{1} pos in map is not right,please check ~-~ 标签 {1} 在地图中的位置不正确，请检查
Cannot detect tag after some distance ~-~ 经过一段距离后无法检测到标签
TagLoc : Only one pgv is allowed for for localization, and now is {1} ~-~ 二维码定位：只允许使用一个 pgv 进行定位，现在数量为 {1}
Tag cannot be seen ~-~ 二维码定位：当前地图中不包含该二维码
No 3D laser pointCloud with current Laser type ~-~ 当前激光类型没有 3D 激光点云
mid360 data empty!!! ~-~ mid360 数据为空!!!
cannot get mid360-data-0!!! ~-~ 无法获得 mid360-data-0!!!
FindCorrespondences err ~-~ 数据关联失败
The robot is not in Tag area, cannot navigate ~-~ 机器人不在标记区域，无法导航

cannot receive Visioscan RD data , from {1} ~-~ Visioscan RD 雷达接收不到数据,IP为: {1}
cannot init Visioscan RD , from {1} ~-~ Visioscan RD 雷达初始化失败,IP为: {1}
cannot receive BlueSea data ~-~ 蓝海(BlueSea)雷达接收不到数据
cannot connect laser with same port :  {1} ~-~ 端口相同的激光无法重复连接:  {1}
cannot connect to laser, because the laser type is not supported : {1} ~-~ 无法连接激光，因为激光类型不支持: {1}
laser lost laser data, and ip: {1} ~-~ 激光丢失数据,IP为:  {1}
LaserFilter ~-~ 激光点云滤波
cannot connect to YDLidar-TG30 ~-~ 无法连接YDLidar-TG30雷达
cannot receive ET laser data ~-~ ET激光雷达接收不到数据
cannot init FocusRay C200 , from {1} ~-~ 富锐 C200 连接失败,IP为:  {1}
cannot receive focusray C200 data , from ~-~ 富锐 C200 接收不到数据,IP为:
cannot init FocusRayh100, from {1} ~-~ 富锐 H100 连接初始化失败 {1}
cannot receive FocusRayH100 data, from {1} ~-~ 富锐 H100 接收不到数据 {1}
Hinson cannot Init driver, from ip : {1} ~-~ 无法打开兴颂(Hinson)雷达，IP为:  {1}
cannot Init Hinson driver ~-~ 兴颂(Hinson)雷达初始化失败
Failed to creat socket driver ~-~ 雷达网络初始化(套接字创建)失败
Failed to bind socket driver ~-~ 雷达网络初始化(套接字绑定)失败
Failed to send socket ~-~ 雷达网络初始化(套接字发送)失败
cannot receive data ~-~ 雷达网络接收不到数据
timeout ~-~ 网络超时
Failed to creat socket driver ~-~ 雷达网络初始化(套接字创建)失败
Failed to bind socket driver ~-~ 雷达网络初始化(套接字绑定)失败
Failed to send socket ~-~ 雷达网络初始化(套接字发送)失败
cannot receive data ~-~ 雷达网络接收不到数据
Failed to creat socket driver ~-~ 雷达网络初始化(套接字创建)失败
Failed to bind socket driver ~-~ 雷达网络初始化(套接字绑定)失败
Failed to send socket ~-~ 雷达网络初始化(套接字发送)失败
cannot receive data ~-~ 雷达网络接收不到数据
cannot Init LANHAI_E200 ~-~ 无法初始化 蓝海LANHAI_E200 雷达
select fail LANHAI_E200 ~-~ 蓝海LANHAI_E200 雷达选择失败
cannot Init N301 SOCKET ~-~ 无法初始化 N301 SOCKET 雷达
cannot Init N301 SOCKET bind ~-~ 无法初始化 N301 SOCKET 雷达
LS_N301 lidar recvfrom timeout ~-~ 星秒 LS N301 SOCKET 雷达接收超时
recvfrom err disconnection ~-~ 雷达连接错误
LS_N301_V1_7 : laser cannot receive data with Compact data type!!! from ~-~ 星秒 LS N301_V1_7 雷达无法接收 Compact 数据类型!!!
LS_N301_V1_7 : laser cannot receive data ~-~ 星秒 LS N301_V1_7 雷达无法接收数据
LS_N301_V1_7 : laser receive data err ~-~ 星秒 LS N301_V1_7 雷达接收数据错误
LS_N301_V1_7 : laser lost connect , from : {1} ~-~ 星秒 LS N301_V1_7 雷达连接丢失,IP为:  {1}
cannot connect laser with current port ~-~ 无法连接激光，当前端口已被占用或者无效
timeout receive laser data from Nanosick, IP: {1} ~-~ 西克 NanoSick 接收激光数据超时,IP为:  {1}
please restart laser, get internal Error with Nanosick, IP: {1} ~-~ 西克 NanoSick 报告内部错误，请重启激光，IP为:  {1}
please clean laser, get Contamination Error with Nanosick, IP: {1} ~-~ 西克 NanoSick 报告污染物错误，请清洁激光，IP为:  {1}
tcp connect error with nano sick ~-~ NanoSick TCP 连接错误
connot Init OLE Socket ~-~ 无法初始化 欧镭 OLE SOCKET 雷达
cannot Init OLE SOCKET bind ~-~ 无法初始化 欧镭 OLE SOCKET 雷达
recvfrom err disconnection ~-~ 雷达连接错误
cannot open olam laser!!! ~-~ 无法打开欧镭激光!!!
timeout receive laser data from olam, IP: {1} ~-~ 欧镭接收激光数据超时,IP为:  {1}
Interal error of olam laser: ~-~ 欧镭激光内部错误:
unable to open ms500 lidar ~-~ 无法打开 MS500 雷达
unable to connect ms500 lidar ~-~ 无法连接 MS500 雷达
unable to get ms500 lidar data ~-~ 无法获取 MS500 雷达数据
cannot connect to R2000 ~-~ 无法连接 R2000 雷达
R2000 disconnected from SRC ~-~ R2000 雷达断开与 SRC 连接
cannot receive laser data within 500 ms ~-~ 雷达接收激光数据超时
pf laser, all data invalid ~-~ 倍加福激光，数据错误。
cannot connect to Sick Laser ~-~ 无法连接西克  Sick Laser 雷达
SICK scan disconnected from SRC ~-~ 西克 SICK 扫描雷达断开与 SRC 连接
Number of laser points is wrong, please reset output range in Sopas ~-~ 激光点数错误，请在西克 Sopas 上位机软件中重置输出范围
cannot connect to S300 ~-~ 无法连接 S300 雷达
TCP Socket creation error ~-~ TCP 套接字创建错误
TCP Connection Error! ~-~ TCP 连接错误!
cannot get picoScan data ~-~ 无法获取西克 PicoScan 数据
picoScan150_New laser cannot receive data with Compact data type!!! from ~-~ 西克 PicoScan150_New 雷达无法接收 Compact 数据类型!!!
picoScan150_New laser cannot receive data ~-~ 西克 PicoScan150_New 雷达无法接收数据
picoScan150_New laser receive data err ~-~ 西克 PicoScan150_New 雷达接收数据错误
cannot connect with Siminics ~-~ 无法连接 Siminics 雷达
cannot connect to urg laser ~-~ 无法连接 URG 雷达
urg has error, please check the light on the scanner or use urg software to check the error ~-~ URG 雷达出现错误，请检查激光扫描头的灯是否亮起，或者使用 URG 软件检查错误。
urg disconnected from SRC ~-~ URG 雷达断开与 SRC 连接
cannot connect with WR Laser ~-~ 无法连接 WR 雷达
VanJee718mini : Failed to connect to laser. Waiting to reconnect! ~-~ 万集 VanJee718mini : 无法连接激光。正在重新连接！
VanJee718mini : Failed to get laser data while 800ms. Waiting to reconnect! ~-~ 万集 VanJee718mini : 800ms 内未收到激光数据。正在重新连接！
cannot Init WanJi driver ~-~ 无法初始化 万集 WanJi 雷达
cannot get WanJi data ~-~ 无法获取 万集 WanJi 数据
scan frequency not match the one you setted,please set 25HZ ~-~ 扫描频率与您设置的不匹配，请设置为 25HZ
cannot Init vanjee_716mini_lidar driver ~-~ 无法初始化 万集 vanjee_716mini_lidar 雷达
cannot Init keli driver ~-~ 无法初始化 科力 Keli 雷达
cannot get KeLi data ~-~ 无法获取 科力 Keli 数据
keli_KLMS laser cannot receive data with Compact data type!!! from {1} ~-~ 科力 Keli_KLMS 雷达无法接收 Compact 数据类型!!! {1}
keli_KLMS laser cannot receive data ~-~ 科力 Keli_KLMS 雷达无法接收数据
keli_KLMS laser receive data err ~-~ 科力 Keli_KLMS 雷达接收数据错误
Lakibeam laser receive lastest package over 1s. ~-~ Lakibeam激光接收最后一包数据超过 1s。
cannot open Lakibeam laser! ~-~ 无法创建与 Lakibeam 激光的通讯。
FocusRay resolution or frequence is not correct, current resolution is {1} from {2} ~-~ 富锐雷达分辨率或频率和当前模型不符 {1} ,来源于 {2}
FocusRay resolution or frequence is not correct, current resolution is {1} from {2} , this laser may is FocueRay H100 , please check ! ~-~ 富锐雷达分辨率或频率和当前模型不符 {1} ,来源于 {2},这可能是富锐H1雷达,请检查确认！
FocusRay resolution or frequence is not correct, current resolution is {1} from {2} , please check that correct FocusRay laser model or configuration is selected ~-~ 富锐雷达分辨率或频率和当前模型不符 {1} ,来源于 {2},请检查确认选中了正确雷达模型！
FocusRay resolution or frequence is not correct, current resolution is {1} from {2}  , this laser may is FocueRay C200 , please check that correct FocusRay laser model or configuration is selected ~-~ 富锐雷达分辨率或频率和当前模型不符 {1} ,来源于 {2},这可能是富锐C2雷达,请检查确认选中了正确雷达模型！
laser frequency : {1} is inconsistent with default frequency : {2}, laser id : {3} ~-~ 雷达当前频率 {1} ,和默认 {2} 不符,雷达ID {3}

odo and laser diff: {1} ms ~-~ 里程时间与激光时间差异过大：{1} ms

[{1}] cannot not get rtcm3 msg from {2}:{3}!error code: {4} ~-~ [{1}] 无法从 {2}:{3} 获取到 rtcm3 数据!错误码: {4}
[{1}] Unable to open serial port: {2}}! ~-~ [{1}] 无法打开串口端口: {2}}!
[{1}] I/O Failed!please checkout UART Device!!! ~-~ [{1}] I/O 错误！请检查串口设备!!!
backend database process error, restart the robot to recover: {1} ~-~ 数据库进程错误，请重启后恢复: {1}
slave id of ModBus TCP, -1 means not specified, take effect after restart ~-~ Modbus TCP的从机ID，-1表示未指定，在重新启动后生效
Threshold for joystick values ~-~ 摇杆值的阈值
Arm GraspLoad to: {1} is illegal ~-~ 机械臂: {1} 非法
Arm Reset: The mb_arm_ctx is NULL ~-~ 机械臂复位：mb_arm_ctx 为空
Arm Reset timeout ~-~ 机械臂复位超时
Arm Reset: {1} ~-~ 机械臂复位: {1}
sound file doesn't exist: ~-~ 音频文件不存在
sound file read failed: ~-~ 音频文件读取失败
Open {1} error, Please clear this error and resubmit the file. ~-~ 打开文件: {1} 错误，请清除错误，重新上传该文件
Set {1} error, Please clear this error and resubmit the file. ~-~ 保存文件: {1} 错误，请清除错误，重新上传该文件
Read {1} error, Please clear this error and resubmit the file. ~-~ 读取文件: {1} 错误，请清除错误，重新上传该文件
Can not load plugin: {1} ~-~ 插件 {1} 加载失败
Hardware authentication failed! ~-~ 控制器硬件校验失败
{1} callService: {2}::{3} error, {4} ~-~ {1} 调用服务 {2}::{3} 出错, {4}
Laser Filter Radius(m) ~-~ 激光滤波器半径(米)
Laser Filter Min Neighbor ~-~ 激光滤波器最小邻居数
Laser Filter Range(m) ~-~ 激光滤波器范围(米)
Multi-pallet recognition method only support CUSTOM_PALLET_TEMPLATE ,POLYGON_TEMPLATE and PALLET_PARAM ~-~
3D measure result has shown there is no Goods on the pallet ~-~
3D measure result has shown goods's width exceeds threshold,which is ~-~
3D measure result has shown goods's height exceeds threshold,which is ~-~
3D measure result has shown goods's width and height exceeds threshold,which width is ~-~
no pallet rec_file can be used ~-~
cannot extract plane from current pointCloud ~-~
score is : ~-~
score pallet is : ~-~
cannot extract plane from current pointCloud after loop all params ~-~
MPC_Q ~-~ MPC精度权重系数
MPC_Q_ANGLE ~-~ 正向运动时MPC角度权重系数
MPC_DELAY ~-~ MPC延迟时间
MPC_R ~-~ MPC速度权重系数
MPC_D ~-~ MPC加速度权重系数
MPC_J ~-~ MPCjerk权重系数
MPC_S ~-~ MPC预测步长
MPC_Q_ANGLE_2 ~-~ 后退时MPC角度权重系数
MPC_PENA ~-~ 侧向偏差的终端惩罚代价
MPC_PENA_ANGLE ~-~ 角度的终端惩罚代价
MPC_PENA_DIST ~-~ 正向运动并且距离终点在此距离内时, 角度权重系数不再生效
g ~-~ 重力加速度
Frictional factor ~-~ 摩擦系数(广义，主要用于过弯时降速)
WheelBase ~-~ 车轮间距
m_walk_motor_max ~-~ 电机最大速度
Free navigation path replace quality threshold ~-~ 路径替换质量阈值
Free navigation max rotation speed (°) ~-~ 最大转向速度
Whether to relax safety constraints to meet kinematic constraints ~-~ 是否放宽安全约束以满足动力学约束
Free navigation loacl planning start distance (m) ~-~ 局部路径规划起始距离
polygon ~-~ 多边形
unknow depth camera: {1}. We set id to 0 ~-~ 未知深度相机{1},将id设置为0
Selected odometer FAILED to initialize ~-~ 选择里程计失败初始化
Selected odometer initialized ~-~ 选择里程计初始化完成
Following error monitor FAILED to initialize ~-~ 跟随错误监视器初始化失败
Odometer FAILED to update using the Message_MotorInfos ~-~ 里程计使用Message_MotorInfos更新失败
Motor following error monitor FAILED to update using the Message_MotorInfos ~-~ 电机跟随错误监视器使用Message_MotorInfos更新失败
Motor following error monitor FAILED to update using the Message_NavSpeed ~-~ 电机跟随错误监视器使用Message_NavSpeed更新失败
beam_index beyond border. beam_index = {1}. now_drop = {2}. user_data.size() = {3}. i = {4}. ScanUsedNum.get() = {5} ~-~ beam_index越界,beam_index={1},now_drop={2},user_data.size()={3},i={4},ScanUsedNum.get()={5}
Bi-steer offset difference calibration localization displacement (m): {1} ~-~ 双向偏差校准定位位移(米):{1}
Bi-steer offset difference calibration localization rotation (deg):{1} ~-~ 双向偏差校准定位旋转(度):{1}
Bi-steer offset difference calibration odometer displacement (m): {1} ~-~ 双向偏差校准里程计位移(米):{1}
Bi-steer offset difference calibration odometer rotation (deg): {1} ~-~ 双向偏差校准里程计旋转(度):{1}
Vehicle moved from ({1}, {2}) to ({3}, {4}) ~-~ 车辆从({1},{2})移动到({3},{4})
ssK0 result: {1} ~-~ ssk0结果：{1}
Optimization result: {1} ~-~ 优化结果：{1}
Clear the .cp values for {1} ~-~ 清除{1}的.cp值
The remaining {1} calibration task(s) will be CANCELED too ~-~ 剩余{1}个标定任务将被取消
Current calibration type {1} not suitable for theta-shaped movement ~-~ 当前标定类型{1}不适用于θ型移动
Theta-shaped movement started the {1} th cycle of all {2} cycle(s) ~-~ θ型移动开始第{1}次，共{2}次
Current calibration type {1} not suitable for one-time listening procedure ~-~ 当前标定类型{1}不适用于一次监听过程
{1} initialized ~-~ {1}初始化完成
{1} continue ~-~ {1}继续
Unexpected state in {1} ~-~ {1}处于意外状态
Current calibration type {1} not suitable for d-shaped movement ~-~ 当前标定类型{1}不适用于d型移动
d-shaped movement parameters confirmation ~-~ d型移动参数确认
The vehicle will go forth and back:\n {1} times with distance ~-~ 车辆将前后左右行走{1}次，每次行走距离
d-Shaped movement start {1}th forward moving ~-~ d型移动开始第{1}次正向移动
d-Shaped movement start {1}th backward moving ~-~ d型移动开始第{1}次反向移动
d-Shaped movement start {1}th forward circling ~-~ d型移动开始第{1}次正转圈
d-Shaped movement start {1}th backward circling ~-~ d型移动开始第{1}次反转圈
Current calibration type ~-~ 当前标定类型
Claw-shaped movement started the ~-~ 爪型移动开始
trajectory error estimator CANNOT handle chassis type {1} ~-~ 轨迹误差估计器不能处理底盘类型{1}
Fitting error during the process is ~-~ 拟合过程中的拟合误差
Fitting error during the calibration process ~-~ 标定过程中的拟合误差
Failed to set listening mode to {1} ~-~ 设置监听模式为{1}失败
Turn on listening mode ~-~ 打开监听模式
Turn off listening mode ~-~ 关闭监听模式
clearCalib {1} ~-~ 清除{1}的标定
CalibrationTask::clearCalib get {1} item(s) ~-~ CalibrationTask::clearCalib获取{1}项
INVALID CalibMoveType {1} to clear results ~-~ INVALID CalibMoveType {1}清除结果
CalibrationTask::setCalibTask get {1} task(s) ~-~ CalibrationTask::setCalibTask获取{1}个任务
Clear the .cp values for {1} ~-~ 清除{1}的.cp值
Clear .cp values for {1} ~-~ 清除{1}的.cp值
External parameters of the IR camera device: {1} ~-~ 外部参数IR相机设备：{1}
Clear the .cp values for{1} ~-~ 清除{1}的.cp值
error_m: {1} ~-~ error_m: {1}
error_f: {1} ~-~ error_f: {1}
Clear .cp values for {1} ~-~ 清除{1}的.cp值
{1} rows of odometer data are recorded during the calibration ~-~ {1}行里程计数据记录在标定过程中
{1} rows of IMU data are recorded during the calibration ~-~ {1}行IMU数据记录在标定过程中
Initial K0 = {1} ~-~ 初始K0 = {1}
IMU Initial calibration results generated: {1} ~-~ IMU初始标定结果生成：{1}
The zero biases of accelerometers in x/y/z axis: {1} ~-~ 加速度计零偏差x/y/z轴：{1}
New IMU position: ({1}, {2}, {3},{4}) ~-~ 新IMU位置：({1},{2},{3},{4})
Clear .cp values for {1} ~-~ 清除{1}的.cp值
New IMU attitude quaterion: ({1}, {2}, {3},{4}) ~-~ 新IMU姿态四元数：({1},{2},{3},{4})
{1} ~-~ {1}
Clear the .cp values for {1} ~-~ 清除{1}的.cp值
Clear .cp values for {1} ~-~ 清除{1}的.cp值
Motor in {1} th quadrant: {2} ~-~ 电机第{1}象限：{2}
Optimization result: {1} ~-~ 优化结果：{1}
Clear the .cp values for {1} ~-~ 清除{1}的.cp值
Clear the .cp values for {1} ~-~ 清除{1}的.cp值
Vehicle will rot around ({1},{2}) ~-~ 车辆绕({1},{2})旋转
Vehicle will rot around (0.0, {1}) ~-~ 车辆绕(0.0,{1})旋转
{1} movement started for PGV calibration ~-~ {1}运动开始PGV标定
PGV calibration data nRows: {1} ~-~ PGV标定数据nRows：{1}
PGV calibration results generated: {1} ~-~ PGV标定结果生成：{1}
The estimated compensation for yaw angle of {1} is {2} deg ~-~ 估计的偏航角{1}的补偿为{2}度
Clear .cp values for {1} ~-~ 清除{1}的.cp值
{1}th backward movement started for PGV-odometer calibration ~-~ {1}次反向运动开始PGV-里程计标定
{1}th counterclockwise rotation started for PGV-odometer calibration ~-~ {1}次逆时针旋转开始PGV-里程计标定
{1}th clockwise rotation started for PGV-odometer calibration ~-~ {1}次顺时针旋转开始PGV-里程计标定
{1}th forward movement started for PGV-odometer calibration ~-~ {1}次正向运动开始PGV-里程计标定
The estimated yaw angle of {1} is {2} (deg) ~-~ 估计的偏航角{1}为{2}度
Clear the .cp values for {1} ~-~ 清除{1}的.cp值
fork tail laser id ~-~ 叉尾激光器id
back laser rec angle. ~-~ 后激光器识别角度。
none ~-~ 无
use two do to control ~-~ 使用两个 DO 来控制
positive DO index ~-~ 正向DO
negative DO index ~-~ 反向DO
one do for reverse, another for enable ~-~ 反向DO（开关动作控制正反方向）和使能DO（打开即电机旋转，关闭即电机停止。）
reverse DO index ~-~ 反向DO（开关动作控制正反方向）
enable DO index ~-~ 使能DO（打开即电机旋转，关闭即电机停止）
delay this time after enable ~-~ 换向后延时该时间开启enableDO
delay this time after reverse ~-~ 运动中延时该时间设置换向DO
negative(e.g. jack down) ~-~ 反方向
positive(e.g. jack up) ~-~ 正方向
buzzer ~-~ 蜂鸣器
buzzer DO index,-1 represent disable ~-~ 蜂鸣器DO序号，-1表示不启用
buzzer time ~-~ 蜂鸣时长
stop time for judge ~-~ 调整停止时间
move delay time ~-~ 移动延迟时间
triColorLight ~-~ 三色灯
red light do index,-1 represent disable \n(suggest DO8 or DO9 when H1.2.10 or later version) ~-~ 红灯 DO 索引，~-~ 1 表示禁用 \n(建议在 H1.2.10 或更高版本时使用 DO8 或 DO9)~-~
interval for red blink ~-~ 红灯闪烁间隔
disable red light when emc ~-~ 当 EMC 时禁用红灯
disable red light when low battery warnning ~-~ 低电量警告时禁用红灯
yellow light do index,-1 represent disable ~-~ 黄灯 DO 索引，-1 表示禁用
interval for yellow light ~-~ 黄灯闪烁间隔
green light do index,-1 represent disable ~-~ 绿灯 DO 索引，-1 表示禁用
interval for green blink ~-~ 绿灯闪烁间隔
cruiseLight ~-~ 巡航灯
cruise light DO index, -1 represent disable ~-~ 巡航灯 DO 索引，-1 表示禁用
enable when in external control mode ~-~ 在外部控制模式下启用
directionLight ~-~ 方向灯
DO,split by SPACE,number represent DO index,0-79 ~-~ DO，以空格分隔，数字表示 DO 索引，0-79
leftForward,split by SPACE,0 represent off, 1 represent on ~-~ 左前方，以空格分隔，0 表示关闭，1 表示开启
rightForward,split by SPACE,0 represent off, 1 represent on ~-~ 右前方，以空格分隔，0 表示关闭，1 表示开启
highSpeedForward,split by SPACE,0 represent off, 1 represent on ~-~ 高速前进，以空格分隔，0 表示关闭，1 表示开启
lowSpeedForward,split by SPACE,0 represent off, 1 represent on ~-~ 低速前进，以空格分隔，0 表示关闭，1 表示开启
leftBackward,split by SPACE,0 represent off, 1 represent on ~-~ 左后退，以空格分隔，0 表示关闭，1 表示开启
rightBackward,split by SPACE,0 represent off, 1 represent on ~-~ 右后退，以空格分隔，0 表示关闭，1 表示开启
backward,split by SPACE,0 represent off, 1 represent on ~-~ 后退，以空格分隔，0 表示关闭，1 表示开启
stop,split by SPACE,0 represent off, 1 represent on ~-~ 停止，以空格分隔，0 表示关闭，1 表示开启
leftSidesWay,split by SPACE,0 represent off, 1 represent on ~-~ 左侧行驶，以空格分隔，0 表示关闭，1 表示开启
rightSidesWay,split by SPACE,0 represent off, 1 represent on ~-~ 右侧行驶，以空格分隔，0 表示关闭，1 表示开启
spinTurn,split by SPACE,0 represent off, 1 represent on ~-~ 旋转转向，以空格分隔，0 表示关闭，1 表示开启
e.g. interval for leftForward, leftBackward and leftSidesWay blink ,0 represent constant light ~-~ 例如，左前方、左后退和左侧行驶闪烁的间隔，0 表示恒定亮度
e.g. interval for rightForward, rightBackward and rightSidesWay blink ,0 represent constant light ~-~ 例如，右前方、右后退和右侧行驶闪烁的间隔，0 表示恒定亮度
angle threshold for left or right ~-~ 左或右的角度阈值
counter for left or right ~-~ 左或右的计数器
threshold for judge high or low speed ~-~ 判断高低速的阈值
x ~-~ x
y ~-~ y
z ~-~ z
qx ~-~ qx
qy ~-~ qy
qz ~-~ qz
qw ~-~ qw
Sensitivity Scale Factor ~-~ 灵敏度缩放因子
cancel task when in external control mode ~-~ 在外部控制模式下取消任务
voltage ~-~ 电压
controller rated voltage ~-~ 控制器额定电压
Controller overvoltage threshold ~-~ 控制器过压阈值
controller warning voltage ~-~ 控制器警告电压
controller error voltage ~-~ 控制器错误电压
controller fault voltage ~-~ 控制器故障电压
How long does it take to shutdown ~-~ 关闭需要多长时间
battery full percentage ~-~ 电池充满百分比
basic ~-~ 基础
before H1.2.10 version: \nNormal id :0-8 \nVirtual id :9-16 \nModbus id :17-80 \n\nbefore H1.2.10 version(include curtis extend IO): \nNormal id :0-16 \nVirtual id :17-24 \nModbus id :25-80 \n\nH1.2.10 or high version: \nNormal id :0-10 \nVirtual id:11-18 \nModbus id :19-80 \n\nH1.2.10 or high version (include curtis extend IO): \nNormal id :0-18 \nVirtual id :19-26 \nModbus id :27-80 ~-~ 在 H1.2.10 版本之前：\n普通 ID：0-8\n虚拟 ID：9-16\nModbus ID：17-80\n\n在 H1.2.10 版本之前（包括 Curtis 扩展 IO）：\n普通 ID：0-16\n虚拟 ID：17-24\nModbus ID：25-80\n\nH1.2.10 或更高版本：\n普通 ID：0-10\n虚拟 ID：11-18\nModbus ID：19-80\n\nH1.2.10 或更高版本（包括 Curtis 扩展 IO）：\n普通 ID：0-18\n虚拟 ID：19-26\nModbus ID：27-80
inverse the trigger level ~-~ 反转触发级别
id ~-~ ID
shape ~-~ 形状
arc ~-~ 弧
yaw ~-~ 偏航
minDist ~-~ 最小距离
maxDist ~-~ 最大距离
range ~-~ 范围
vertex ~-~ 顶点
posX1 ~-~ X1位置
posY1 ~-~ Y1位置
type ~-~ 类型
collision ~-~ 碰撞
infrared ~-~ 红外线
ultrasonic ~-~ 超声波
fallingDown ~-~ 倾倒
func ~-~ 功能
stop ~-~ 停止
slowdown ~-~ 减速
source ~-~ 源
DI ~-~ 数字输入
DI index ~-~ 数字输入索引
DO ~-~ 数字输出
DO index ~-~ 数字输出索引
EMC button ~-~ EMC按钮
externalControl ~-~ 外部控制
manipulatorConnect ~-~ 操作手连接
motorInfo ~-~ 电机信息
motorName ~-~ 电机名称
enable check current ~-~ 启用检查电流
current threshold ~-~ 电流阈值
enable check temp ~-~ 启用检查温度
temperature ~-~ 温度
enable check stop ~-~ 启用检查停止
enable check err ~-~ 启用检查错误
enable check emc ~-~ 启用检查 EMC
hexadecimal, e.g. 0x98 ~-~ 十六进制，例如 0x98
errCode ~-~ 错误码
error code, e.g. 52110 ~-~ 错误码，例如 52110
risingEdge ~-~ 上升沿
fallingEdge ~-~ 下降沿
suspendTask ~-~ 挂起任务
resumeTask ~-~ 恢复任务
cancelTask ~-~ 取消任务
releaseControl ~-~ 释放控制
recycleControl ~-~ 回收控制
powerOffDriver ~-~ 关闭驱动器
powerOnDriver ~-~ 打开驱动器
openDO ~-~ 打开数字输出(DO)
DO index ,-1 represent disable ~-~  DO索引，-1代表禁用
closeDO ~-~  关闭DO
DOindex ,-1 represent disable ~-~  DO索引，-1代表禁用
switchToSRCControl ~-~  切换到SRC控制
switchToExternalControl ~-~  切换到外部控制
navToTarget ~-~  导航至目标
target point, only letters and numbers ~-~  目标点，仅限字母和数字
resetMotor ~-~  重置电机
motorName, only motor can be calibrated ~-~  电机名称，仅电机可以被校准
clearMotorFault ~-~  清除电机故障
motorName, only motor can be cleared err ~-~  电机名称，仅电机可以被清除错误
toggleDO ~-~  切换DO
enableMotor ~-~  启用电机
motorName, only motor can be enabled(conflict with EMC driver protocol EMC) ~-~  电机名称，仅电机可以被启用（与EMC驱动协议EMC冲突）
disableMotor ~-~  禁用电机
motorName, only motor can be disabled(conflict with EMC driver protocol EMC) ~-~  电机名称，仅电机可以被禁用（与EMC驱动协议EMC冲突）
runScript ~-~  运行脚本
name ~-~  名称
args ~-~  参数
clearErrorCode ~-~  清除错误代码
user range:error: 53900~53999,warning:55900~55999-1 represent disable ~-~  用户范围：错误：53900〜53999，警告：55900〜55999-1代表禁用
setErrorCode ~-~  设置错误代码
error string ~-~  错误字符串
repowerDriver ~-~  重新上电驱动器
delay before power off ~-~  关闭电源前的延迟
delay before power on ~-~  上电前的延迟
reopenDO ~-~  重新打开DO
delayBeforeCloseDO ~-~  关闭DO前的延迟
delayBeforeOpenDO ~-~  打开DO前的延迟
clear motor encoder ~-~  清除电机编码器
motorName, nly motor can be cleared encoder ~-~  电机名称，仅电机可以清除编码器
calibGrip ~-~  校准夹爪
gripName, only grip can be calib ~-~  夹爪名称，仅夹爪可以被校准
reloc service from pose ~-~  从姿态重新定位服务
location mark point ~-~  位置标记点
basic parameters ~-~  基本参数
before H1.2.10: \nNormal id :0-6 \nreserve :7-14 \nModbus id :15-79 \n\nH1.2.10 or later: \nNormal id :0-9 \nreserve:10-17 \nModbus id :18-79\n(DO8 DO9 output level 400mA) ~-~  在H1.2.10之前：\n普通ID：0-6\n保留：7-14\nModbus ID：15-79\n\nH1.2.10或更高版本：\n普通ID：0-9\n保留：10-17\nModbus ID：18-79\n（DO8 DO9输出电平400mA）
default ~-~  默认
measure ~-~  测量
MeasureLoad1 ~-~  测量负载1
MeasureADC1 ~-~  测量ADC1
MeasureLoad2 ~-~  测量负载2
MeasureADC2 ~-~  测量ADC2
interval for start, -1 represent disable ~-~  启动间隔，-1代表禁用
DO array, spilt by SPACE, only number, please disable DO device default, range 0-79 ~-~  DO数组，以空格分隔，仅数字，请将DO设备默认禁用，范围0-79
Take back control ~-~  收回控制权
When the CAN bus reports an error, the EMC causes the motor to lose power ~-~  当CAN总线报告错误时，EMC导致电机失去电源
Unplug the EMC to continue the task ~-~  拔出EMC以继续任务
Cancel the task ~-~  取消任务
function ~-~  功能
The drive uses I/O EMC mode ~-~  驱动器使用I/O EMC模式
Protocol disabled (Trigger Do not use this function when enableMotor or disableMotor is configured on the device) ~-~  协议禁用（触发器 当在设备上配置enableMotor或disableMotor时，请勿使用此功能）
Gripper device id(can not repeat) ~-~  夹持器设备ID（不能重复）
grip force value ~-~  夹持力值
grip running speed ~-~  夹持运行速度
brand ~-~  品牌
/dev/ttyxxx for rs485 ~-~  RS485的/dev/ttyxxx
G ~-~  G
U ~-~  U
V ~-~  V
fx0 ~-~  fx0
fy0 ~-~  fy0
fz0 ~-~  fz0
mx0 ~-~  mx0
my0 ~-~  my0
mz0 ~-~  mz0
Baud rate ~-~  波特率
The Modbus IO is not connected CTX NULL ~-~  Modbus IO未连接 CTX NULL
The Modbus IO is not connected connection=-1 ~-~  Modbus IO未连接 连接=-1
controller voltage is: ~-~  控制器电压为：
lower than the controller rated voltage ~-~  低于控制器额定电压
lower than the controller rated voltage, controller will shutdown after ~-~  低于控制器额定电压，控制器将在之后关闭
Higher than the controller rated voltage ~-~  高于控制器额定电压
Motor Disable: ~-~  电机禁用：
Motor Error: ~-~  电机错误：
Linear Limit Triggered: ~-~  线性限位触发：
Rotation Limit Triggered: ~-~  旋转限位触发：
linear motor upReached DI and downReached DI status is error! ~-~  线性电机达到上限DI和下限DI状态错误！
enable Modbus IO extend module ~-~  启用Modbus IO扩展模块
ip of Modbus IO extend module ~-~  Modbus IO扩展模块的IP
port of Modbus IO extend module ~-~  Modbus IO扩展模块的端口
offset of digital output for Modbus IO ~-~  Modbus IO数字输出的偏移量
offset of digital input for Modbus IO ~-~  Modbus IO数字输入的偏移量
number of digital output for Modbus IO ~-~  Modbus IO数字输出的数量
number of digital input for Modbus IO ~-~  Modbus IO数字输入的数量
debug for test speed ~-~  测试速度的调试
astern alarm flag ~-~  倒车警报标志
debug for odometer ~-~  里程表的调试
debug for sonic ~-~  超声波的调试
debug for RFID ~-~  RFID的调试
debug for magnetic sensor ~-~  磁传感器的调试
debug for digital input ~-~  数字输入的调试
debug for encoder ~-~  编码器的调试
debug for Modbus IO ~-~  Modbus IO的调试
debug for PGV ~-~  PGV的调试
PgvPrintOrigData ~-~  PgvPrintOrigData
pgv log freq ~-~  pgv日志频率
When switching internal and external control modes, do not consider whether the car body is stopped or not ~-~  切换内部和外部控制模式时，不考虑车身是否停止
battery source choosen by soc ~-~  由soc选择的电池源
max voltage when full percent ~-~  满百分比时的最大电压
min voltage when empty percent ~-~ 空置时的最低电压百分比
speed ratio for chassis move ~-~ 底盘移动的速度比例
fork pressure debug framrate ~-~ 货叉压力调试帧率
motor print debug counter ~-~ 电机打印调试计数器
imu print debug counter ~-~ IMU打印调试计数器
return navspeed debug ~-~ 返回导航速度调试
buzzer info ~-~ 蜂鸣器信息
net debug ~-~ 网络调试
DistanceSensor Log Freq ~-~ 距离传感器日志频率
flag for dmx512 led test ~-~ DMX512 LED测试标志
Gripper debug ~-~ 夹爪调试
GripperPrintOrigData ~-~ 夹爪打印原始数据
Gripper log freq ~-~ 夹爪日志频率
ForceSensor debug ~-~ 力传感器调试
ForceControlPrintOrigData ~-~ 力控制打印原始数据
ForceSensor log freq ~-~ 力传感器日志频率
SRC can not switch mode while moving ~-~ 移动时无法切换SRC模式
Reset motor should in state when all motors are stopped. ~-~ 当所有电机停止时，应将电机复位
Don't setDO(normal) when movetask unreleased DO.(DOMotor used) ~-~ 在movetask未释放DO时不要设置DO（正常）。（使用DOMotor）
Don't setDO(modbus) when movetask unreleased DO.(DOMotor used) ~-~ 在movetask未释放DO时不要设置DO（modbus）。 （使用DOMotor）
MotorCmd missed: ~-~ 丢失MotorCmd：
Rec NaN value: ~-~ 收到NaN值：
illegal speed, vx: ~-~ 非法速度，vx：
vibration occurs when robot is stationary ~-~ 机器人静止时发生震动
Please check the path of steerOffsetFile in 'model-motor-steer' ~-~ 请检查'model-motor-steer'中steerOffsetFile的路径
DOMotor is calibrating ~-~ DOMotor正在校准
DOMotor calibration timeout ~-~ DOMotor校准超时
DOMotor zeroDI must be configured ~-~ 必须配置DOMotor zeroDI
DOMotor positiveDO or negativeDO or enableDO must be configured ~-~ 必须配置DOMotor positiveDO或negativeDO或enableDO
DOMotor ~-~ DOMotor
negative ~-~ 负
positive ~-~ 正
limit triggered ~-~ 触发限制
ZJ led timeout, please check the pin of ~-~ ZJ LED超时，请检查引脚
Steer reductionRatio should not be zero ~-~ 转向减速比不应为零
Walk reductionRatio should not be zero ~-~ 行走减速比不应为零
EtherCAT Motor newspeed timeout! ~-~ EtherCAT电机新速度超时！
EtherCAT MOtorSlowdown finished ~-~ EtherCAT MOtorSlowdown完成
WST-SM16512PS-DMX512 ~-~ WST-SM16512PS-DMX512
script name+.py,如test.py ~-~ 脚本名称+.py，如test.py
colorRed proportion ~-~ 红色比例
colorGreen proprotion ~-~ 绿色比例
colorBlue proprotion ~-~ 蓝色比例
colorWhite proprotion ~-~ 白色比例
enable show charging ~-~ 启用显示充电
enable show battery percentage ~-~ 启用显示电池百分比
turnLeftFront DO index（6 led/set） ~-~ 左前转向DO索引（6个led/组）
turnLeftFront DO num（6 led/set） ~-~ 左前转向DO数量（6个led/组）
turnLeftRear DO index（6 led/set） ~-~ 左后转向DO索引（6个led/组）
turnLeftRear DO num（6 led/set） ~-~ 左后转向DO数量（6个led/组）
turnRightFront DO index（6 led/set） ~-~ 右前转向DO索引（6个led/组）
turnRightFront DO num（6 led/set） ~-~ 右前转向DO数量（6个led/组）
turnRightRear DO index（6 led/set） ~-~ 右后转向DO索引（6个led/组）
turnRightRear DO num（6 led/set） ~-~ 右后转向DO数量（6个led/组）
led total num（6 led/set） ~-~ LED总数（6个led/组）
white breath when back ~-~ 背面白色呼吸灯
red channel map ~-~ 红色通道映射
green channel map ~-~ 绿色通道映射
blue channel map ~-~ 蓝色通道映射
white channel map ~-~ 白色通道映射
YM-SM16512PS-DMX512 ~-~ YM-SM16512PS-DMX512
LogofrontPos DO index（6 led/set） ~-~ 前置DO索引（6个led/组）
LogofrontNum DO num（6 led/set） ~-~ 前置DO数量（6个led/组）
LedRight1Pos DO index（6 led/set） ~-~ 右侧1号DO索引（6个led/组）
LedRight1Num DO num（6 led/set） ~-~ 右侧1号DO数量（6个led/组）
LogoRightPos DO index（6 led/set） ~-~ 右侧标志DO索引（6个led/组）
LogoRightNum DO num（6 led/set） ~-~ 右侧标志DO数量（6个led/组）
LedRight2Pos DO index（6 led/set） ~-~ 右侧2号DO索引（6个led/组）
LedRight2Num DO num（6 led/set） ~-~ 右侧2号DO数量（6个led/组）
LogoBackPos DO index（6 led/set） ~-~ 后部标志DO索引（6个led/组）
LogoBackNum DO num（6 led/set） ~-~ 后部标志DO数量（6个led/组）
LedLeft1Pos DO index（6 led/set） ~-~ 左侧1号DO索引（6个led/组）
LedLeft1Num DO num（6 led/set） ~-~ 左侧1号DO数量（6个led/组）
LogoleftPos DO index（6 led/set） ~-~ 左侧标志DO索引（6个led/组）
LogoleftNum DO num（6 led/set） ~-~ 左侧标志DO数量（6个led/组）
LedLeft2Pos DO index（6 led/set） ~-~ 左侧2号DO索引（6个led/组）
LedLeft2Num DO num（6 led/set） ~-~ 左侧2号DO数量（6个led/组）
private led ~-~ 私有LED
decDistFar ~-~ 远距离
decDistNear ~-~ 近距离
ZJ-LED-RGB-CTRL ~-~ ZJ LED RGB 控制
Use scripts to fit the leds ~-~ 使用脚本适配LED灯
id(only use once) ~-~ ID（仅使用一次）
minRSSI ~-~ 最小RSSI
maxRSSI ~-~ 最大RSSI
BeneWake-TFmini-i ~-~ BeneWake TFmini-i
Elco-OSM4x-485 ~-~ Elco OSM4x-485
port ~-~ 端口
can1 ~-~ CAN1
can2 ~-~ CAN2
rs485 ~-~ RS485
terminator ~-~ 终止符
Timeout error time, unit:s ~-~ 超时错误时间，单位：秒
The number of consecutive times is determined as charging. The default value is 0. The detection count is once every second ~-~ 连续充电次数确定。默认值为0。检测次数每秒一次。
Power filter threshold ~-~ 电源滤波器阈值
The value of the time maintained after shutdown ~-~ 关闭后保持时间的值
In this mode, you need to configure parameters such as the baud rate using the net2Serial device ~-~ 在此模式下，您需要使用net2Serial设备配置诸如波特率之类的参数
In this mode, you need to configure parameters such as the baud rate on the byNet2Can device ~-~ 在此模式下，您需要在byNet2Can设备上配置诸如波特率之类的参数
EtherCAT parameter ~-~ EtherCAT参数
Enable EtherCAT ~-~ 启用EtherCAT
EtherCAT slaves support dynamic pdo mapping ~-~ EtherCAT从站是否支持动态PDO映射
The position on ethercat bus ~-~ EtherCAT总线索引
EtherCAT vendor id ~-~ EtherCAT厂商ID
EtherCAT product id ~-~ EtherCAT产品ID
This value is used to transform the unit(cnt/s) in application layer to the unit(eg:rpm) of 0x60FF ~-~ 该值用于将应用层的单位(cnt/s)转换为最大不超过0x60FF的单位(例如:rpm)
This value is used to transform the unit(deg/s^2) in application layer to the unit(eg:rpm) of 0x6081 ~-~ 该值用于将应用层的单位(deg/s^2)转换为最大的不超过0x6081的单位(例如:rpm)
use battery internal relay ~-~ 控制电池内部充电继电器
interlock when jack and walk ~-~ 行走和举升电机互锁
slow time when newspeed timeout triggered ：NewSpeedTimeoutSlowT*20 ms ~-~ 当下发新的速度命令超时时，减速停车的时间将会被配置为本参数*20毫秒
enable warning light ~-~ 启用警示灯
calibration is running ~-~ 标定进行中
whether recoder odometer can frame ~-~ 是否记录里程计CAN报文帧
whether is the status that ready to move ~-~ 是否处于可以移动的状态
to judge the gyro if flying ~-~ 陀螺仪漂移阈值
freq of query for enable and error ~-~ 查询使能和故障的频率
don't clean error that motor disable or error ~-~ 不清除电机禁用或错误
Spin use dynamic calibrating when pass zeroDI ~-~ 旋转电机在通过zeroDI时使用动态标定校准
spin error ~-~ 旋转电机错误
Spin Reversal calib velocity after spin zeroDI triggered ~-~ 旋转电机在zeroDI触发方向反转时二次校准速度
receive nothing in report UDP thread ~-~ 在UDP线程中未接收到任何内容
can not connect to DIO board ~-~ 无法连接到DIO板
Heart broken ~-~ 心跳丢失
DSP reconfiging( ~-~ DSP重新配置中
get gyro version error ~-~ 获取陀螺仪版本错误
DSP version too low ~-~ DSP版本过低
get firmware version error ~-~ 获取固件版本错误
EtherCAT Motor ignore Navspeed in Slowdown ~-~ EtherCAT电机在减速停车过程中忽略控制下发速度
Controller emergency stop ~-~ 控制器急停
heart beat recv timeout ~-~ 心跳接收超时
feature is not in SRC800- ~-~ SRC800不支持该功能
src800 activation has problem! ~-~ SRC800激活故障
battery brand not matches with Uart type. ~-~ 该电池品牌不是串口(uart)通信类型
battery errcode 0x ~-~ 电池错误码0x
UART Battery response time out ~-~ UART电池响应超时
battery brand not matches with CAN type ~-~ 该电池品牌不是CAN通信类型
The canPort in can battery is empty! ~-~ CAN电池中的canPort为空！
battery warning 0x ~-~ 电池警告0x
CAN Battery response time out ~-~ CAN电池响应超时
distanceSensor Timeout: ~-~ 距离传感器超时：
Error in Gyro. No data received. GyroBase.cpp ~-~ 陀螺仪超时且未接收到数据
Motor calibration is timeout ~-~ 电机校准超时
Linear reductionRatio should big than 0 ~-~ 线性电机减速比应大于0
Linear Motor does not support calibrate by driver currently ~-~ 线性电机目前不支持通过驱动器校准
linear calibration use byDriver, ensure the zero di whether < 0 ~-~ 线性电机通过驱动器标定，请确保零位di是否<0
linear calibration use bySpeed, ensure the zero di whether >= 0 ~-~ 线性电机通过速度标定，确保零位di是否>=0
motor ~-~ 电机
is not supported ~-~ 不支持
Rotation reductionRatio should big than 0 ~-~ 旋转电机减速比应大于0
Rotation Motor does not support calibrate by driver currently ~-~ 旋转电机目前不支持通过驱动器校准
rotation calibration use bySpeed, ensure the zero di whether >= 0 ~-~ 旋转电机通过速度标定，请确保零位di是否>=0
Spin reductionRatio should not be zero ~-~ 旋转电机减速比不应为零
Spin Motor does not support calibrate by driver currently ~-~ 旋转电机目前不支持通过驱动器校准
have not support calibration by driver yet ~-~ 尚未支持通过驱动器校准
Spin motor's block di triggered in calibrating ~-~ 旋转电机在标定过程中触发了停止DI
Moons MDX watch dog triggered ~-~ 鸣志MDX型号驱动器看门狗触发
New speed timeout! ~-~ 控制下发新的速度命令超时！
Slowdown finished ~-~ 减速停车完成
Motor initialize is timeout ~-~ 电机初始化超时
motor do not support 'driver protocol EMC' ~-~ 该电机不支持"驱动器急停协议"
newspeedtimeout timer threshold ~-~ 接收速度更新指令超时定时器阈值配置
threshold for motor timeout ~-~ 电机超时阈值配置
newspeed timeout deceleration time after triggering: NewSpeedTimeoutSlowT*20 ms ~-~ 触发后接收速度指令超时后的减速时间：该配置项*20毫秒
the frequency of query encoder ~-~ 查询编码器的频率
the frequency of send watchdog ~-~ 发送看门狗的频率
Ignore Navspeed in Slowdown ~-~ 在减速时忽略导航下发速度
IsExternalControlv2 ~-~ v2版本外部控制
flag of can0dump starting log the file canlog.log to log folder ~-~ 开始记录can0报文到日志文件夹中canlog.log的标志
flag of can1dump starting log the file canlog.log to log folder ~-~ 开始记录can1报文到日志文件夹中canlog.log的标志
SM16512 chip led ~-~ SM16512型号灯带
theme colors: red ~-~ 主题颜色：红色
theme colors: green ~-~ 主题颜色：绿色
theme colors: blue ~-~ 主题颜色：蓝色
theme colors: white ~-~ 主题颜色：白色
Whether to display the charging effect ~-~ 是否显示充电效果
Indicates whether the battery level is displayed ~-~ 是否显示电池电量
Left front steering light set serial number(6 led/group) ~-~ 【TODO 括号中的描述】左前转向灯组序列号(6 led/组)
Number of left front steering lights(6 led/group) ~-~ 左前转向灯数量(6 led/组)
Left rear turn lights serial number(6 led/group) ~-~ 左后转向灯组序列号(6 led/组)
Number of left rear steering lights(6 led/group) ~-~ 左后转向灯数量(6 led/组)
Right front turn lights serial number(6 led/group) ~-~ 右前转向灯组序列号(6 led/组)
Right front turn number of lights(6 led/group) ~-~ 右前转向灯数量(6 led/组)
Right rear turn lights serial number(6 led/group) ~-~ 右后转向灯组序列号(6 led/组)
Right rear turn number of lights(6 led/group) ~-~ 右后转向灯数量(6 led/组)
Number of lamp bead groups(6 led/group) ~-~ 灯珠组数量(6 led/组)
CMD4A2 led ~-~ CMD4A2灯带
collision pressure threshold ~-~ 碰撞压力阈值
CAN base id offset ~-~ CAN ID偏移
can port ~-~ CAN口
can port1 ~-~ CAN口1
can port2 ~-~ CAN口2
min dist ~-~ 【TODO 单位】最小距离（单位：米）
max dist ~-~ 最大距离（单位：米）
zero offset ~-~ 零飘
Emission Angle ~-~ 发射角
min RSSI ~-~ 最小接收信号强度
max RSSI ~-~ 最大接收信号强度
Panasonic-HG-C1000 ~-~ 松下HG-C1000
communicate port ~-~ 通信端口
M4 CAN ~-~ M4 CAN
DSP RS485 port ~-~ DSP RS485 通信端口
M4 RS485 port ~-~ M4 的RS485端口
M4 uart supports only: /dev/M4Uart2 , /dev/M4Uart3 , /dev/M4Uart4 and /dev/M4Uart5 ~-~ M4 的串口仅支持以下名称：/dev/M4Uart2 , /dev/M4Uart3 , /dev/M4Uart4 and /dev/M4Uart5
BaiWei-Bwbm617-ProtocolA5 ~-~ baiwei A5 版电池协议
BaiWei-CAN-PrivateCan ~-~ BaiWei 私有 CAN 电池协议
DaLi-V1-Protocol ~-~ DaLi私有电池协议
Dazhong-THLD-Protocol ~-~ Dazhong私有电池协议
foxconn-None-Private ~-~ 富士康私有电池协议
JiaBaiDa-V4-Private ~-~ jiabaida私有电池协议
LTW-None-Private ~-~ 力通威私有电池协议
muxing-private-can-battery ~-~ 牧星私有 CAN 电池协议
SuRay-485-Private ~-~ 速锐 RS485 私有电池协议
TiTans-None-PrivateCan ~-~ 天太私有 CAN 电池协议
TopBand-TB4840F-WwPrivate ~-~ 拓邦 私有电池协议
LiPin-Fork-Protocol1363 ~-~ 锂平货叉私有电池协议
capacity ~-~ 容量
/dev/ttyxxx for rs232 ~-~ /dev/ttyxxx用于RS232
canPort ~-~ can端口
port1 ~-~ 端口1
port2 ~-~ 端口2
port3 ~-~ 端口3
baudrate ~-~ 波特率
mode ~-~ 模式
differential ~-~ 差分
wheelNum ~-~ 轮数
omni ~-~ 全向
steer ~-~ 转向
multiSteers ~-~ 多路转向
encoder line ~-~ 编码器线
current factor ~-~ 电流系数
up Limit DI ~-~ 上限DI
down Limit DI ~-~ 下限DI
Zero DI ~-~ 零位DI
position Speed ~-~ 位置速度
walk ~-~ 行走
minimum starting speed ~-~ 最小启动速度
deltaCnt ~-~ delta计数
deadDealerK ~-~ 死亡商人K
delay for deadDealer ~-~ 死亡商人延迟
linear ~-~ 线性
upViscousSpeed ~-~ 上升粘性速度
upSpeedBias ~-~ 上升速度偏差
outEncoder ~-~ 输出编码器
out Encoder Ratio ~-~ 输出编码器比率
out Encoder Line ~-~ 输出编码器线
resetMode ~-~ 重置模式
motor calib feedback ~-~ 电机校准反馈
curtis Steer Range ~-~ Curtis转向范围
ELMO-Canopen ~-~ ELMO Canopen
ESTUN-DC10BMG-CANOpen ~-~ ESTUN DC10BMG CANOpen
JMC-C830RC-CANOpen ~-~ JMC C830RC CANOpen
heartbeatCycleCount ~-~ 心跳周期计数
Moons-MDX-SeerCANOpen ~-~ Moons MDX SeerCANOpen
Moons-M2DC-CANOpen ~-~ Moons M2DC CANOpen
MOON-MBDV-CANOpen ~-~ MOON MBDV CANOpen
TianTai-LVSI-CANOpen ~-~ TianTai LVSI CANOpen
TianTai-LVSI-CANOpenPDO ~-~ TianTai LVSI CANOpenPDO
ReBoTe-ZAPI-AceCOMBIX ~-~ ReBoTe ZAPI ACECOMBIX
ZLTECH-ZLAC8030L-CANOpen ~-~ ZLTECH ZLAC8030L CANOpen
XINJIE-DF3E4010-CANOpen ~-~ XINJIE DF3E4010 CANOpen
Curtis-F2A-HeLi ~-~ Curtis F2A HeLi
outEncoderBrand ~-~ 输出编码器品牌
out Encoder Single-Trun Resolution Ratio ~-~ 输出编码器单次转动分辨率比率
out Encoder Multi-Trun Resolution Ratio ~-~ 输出编码器多次转动分辨率比率
PEPPERL-ENA36-CANOpen ~-~ PEPPERL ENA36 CANOpen
PEPPERL-CVS58-CANOpen ~-~ PEPPERL CVS58 CANOpen
BANNER-BEH36-CANOpen ~-~ BANNER BEH36 CANOpen
IDENCODER-A38L6-CANOpen ~-~ IDENCODER A38L6 CANOpen
SICK-AHM36-CANOpen ~-~ SICK AHM36 CANOpen
TOFI-LCF80J-CANOpen ~-~ TOFI LCF80J CANOpen
Curtis-1232-RuiBoTe ~-~ Curtis 1232 RuiBoTe
Curtis-1298-Seer ~-~ Curtis 1298 Seer
Curtis-1232-HeLi ~-~ Curtis 1232 HeLi
Kinco-FD-CANOpen ~-~ Kinco FD CANOpen
normal install ~-~ 正常安装
HIKVISION-02MWG-485 ~-~ HIKVISION 02MWG 485
HIKVISION-SC-485 ~-~ HIKVISION SC 485
HIK Code reading compensation time ~-~ HIK代码读取补偿时间
DaHua-R3051-485 ~-~ DaHua R3051 485
mindeo-ES4880S-GLB ~-~ mindeo ES4880S GLB
pgv in y direction ~-~ pgv在y方向上
MuXing-pgv-485 ~-~ MuXing pgv 485
MS Code reading compensation time ~-~ MS代码读取补偿时间
EtherCAT motor timeout ~-~ EtherCAT电机超时
EtherCAT motor new speed timeout ~-~ EtherCAT电机接收速度超时
Cannot receive frame for a few time ~-~ 收不到数据帧
Cannot receive MoveFactory instruction for a few time ~-~ 无法接收 MoveFactory 的指令
Check EtherCAT bus or the power of motor servo ~-~ 检查 EtherCAT 总线或伺服电机电源
Contact SEER ~-~ 联系 SEER
parse error: {1} ~-~ 解析错误: {1}
The Goal has goods. Cannot unLoad!!! DI: {1} ~-~ 目标有货物。无法放货! DI: {1}
No Jack Module ~-~ 没有顶升模块
parse error in body : {1} ~-~ 主体解析错误: {1}
The Skill name is wrong: {1} ~-~ 技能名称错误: {1}
Arm init model is null ~-~ 机械臂初始化模型为空
Avoid init model is null ~-~ 避障初始化模型为空
ChargerOff init model is null ~-~ 充电器关闭初始化模型为空
Charger status error!. Charger name is {1} Status is {2} ~-~ 充电器状态错误! 充电器名称是{1} 状态是{2}
CollisionCheck init model is null ~-~ 碰撞检查初始化模型为空
Jack byController Mode. Cannot Find Linear Motor. ~-~ 顶升使用控制器模式。找不到线性电机。
all Motors are empty! ~-~ 所有电机都为空!
jack target too low. min_jack_height = {1} send_height = {2} ~-~ 顶升目标高度太低。最小顶升高度 = {1} 发送高度 = {2}
jack target too hight. max_jack_height = {1} send_height = {2} ~-~ 顶升目标高度太高。最大顶升高度 = {1} 发送高度 = {2}
Jack byController Mode. Cannot Find Linear Motor: {1} ~-~ 顶升使用控制器模式。找不到线性电机: {1}
Can't open Recfile, while ControllerJack. File: {1} ~-~ 无法打开识别文件，当顶升使用控制器模式。文件: {1}
ControllerJack init model is null ~-~ 控制器模式顶升初始化模型为空
Action Over Time {1} ~-~ 动作超时 {1}
Can't open Recfile, while DOJack. File: {1} ~-~ 无法打开记录文件，当顶升使用 DO 模式。文件: {1}
DOJack init model is null ~-~ DO 模式顶升初始化模型为空
Jack model doesn't config completely ~-~ 顶升模型配置不完整
Jack byDO doesn't support cmd:{1} ~-~ 顶升使用 DO 模式不支持命令:{1}
Jack counter point DI not triggered ~-~ 顶升计数 DI 未触发
DirAdjust init model is null ~-~ 方向调整初始化模型为空
DisableMotor init model is null ~-~ 禁用电机初始化模型为空
ForkDi init model is null ~-~ ForkDi 初始化模型为空
Fork Cannot Load Again. ContactDi is True. ~-~ 叉车无法再次取货。货物检测 DI 已触发。
The Goal has goods. Cannot unLoad!!! DI: {1} ~-~ 目标有货物。无法放货! DI: {1}
ForkDi Over Time {1} ~-~ ForkDi 超时 {1}
Unload, But the destination has goods! ~-~ 放货，但目的地有货物!
topDI {1} is larger than max DI number: {2} ~-~ 上 DI {1} 大于最大DI编号: {2}
bottomDI {1} is larger than max DI number: {2} ~-~ 下 DI {1} 大于最大DI编号: {2}
ForkForward init model is null ~-~ ForkForward 初始化模型为空
ForkHeight init model is null ~-~ ForkHeight 初始化模型为空
Read fork minHeight or maxHeight Error! {1} ~-~ 读取叉车最小高度或最大高度错误! {1}
fork target too low. min_fork_height = {1} send_height = {2} ~-~ 叉车目标高度太低。最小叉车高度 = {1} 发送高度 = {2}
fork target too hight. max_fork_height = {1} send_height = {2} ~-~ 叉车目标高度太高。最大叉车高度 = {1} 发送高度 = {2}
Fork byController Mode. Cannot Find Linear Motor: {1} ~-~ 叉车抬升使用控制器模式。找不到线性电机: {1}
Fork byController Mode. Cannot Find Fork Motor ~-~ 叉车抬升使用控制器模式。找不到线性电机
setFork Fail ~-~ 设置货叉失败
Goods on the fork is over weight. {1} {2} ~-~ 叉车上的货物超重。{1} {2}
ForkHeight Over Time {1} ~-~ 叉车调整高度超时 {1}
there is no enough layer: need layer( {1} ), recognize layer( {2} ). ~-~ 没有足够的层: 需要层( {1} ), 识别层( {2} )。
Fork down too much with ultraSonic DI open. ~-~ 超声波DI开启叉齿下降太多。
ForkLift init model is null ~-~ ForkLift 初始化模型为空
Fork module's Motors are empty! ~-~ 叉车模块的电机为空!
operation name error: {1}. Should be 'height', 'load', 'unload' ~-~ 动作名称错误: {1}。应该是 'height', 'load', 'unload'
operation should be string!!! ~-~ 动作应该是字符串!!!
no operation!!! ~-~ 没有该动作!!!
FreeGo init model is null ~-~ 自由导航初始化模型为空
target id is null ~-~ 目标 ID 为空
target x is null ~-~ 目标 X 为空
target y is null ~-~ 目标 Y 为空
target theta is null ~-~ 目标角度为空
no freeGo ~-~ 没有自由导航
GetBattery init model is null ~-~ 获取电池初始化模型为空
rec fail reach max times: {1} ~-~ 识别失败达到最大次数: {1}
adjust fail reach max times: {1} ~-~ 调整失败达到最大次数: {1}
Cannot Recognize Battery! ~-~ 无法识别电池!
recognition result is invalid {1} ~-~ 识别结果无效 {1}
Can't read Recfile. File: {1} {2} {3} {4} {5} {6} {7} ~-~ 无法读取识别文件。文件: {1} {2} {3} {4} {5} {6} {7}
GoDistance init model is null ~-~ GoDistance 初始化模型为空
GoForkPath INIT model is null ~-~ GoForkPath 初始化模型为空
GoPGV init model is null ~-~ GoPGV 初始化模型为空
PGV Method Based On Code Doesn't Support pgv_adjust_dist paramter!!! ~-~ 基于二维码的 PGV 方法不支持 pgv_adjust_dist 参数!!!
pgv adjust reaches max times. {1} ~-~ pgv调整达到最大次数。{1}
Cannot open blinkDO: {1} ~-~ 无法打开 blinkDO: {1}
PGV cannot find code. ~-~ PGV找不到代码。
PGV cannot find code ~-~ PGV找不到代码
GoPath init model is null ~-~ GoPath 初始化模型为空
GoPathCharge init model is null ~-~ GoPathCharge 初始化模型为空
Charge device is not enable! ~-~ 充电设备未启用!
charger hardware problem ~-~ 充电桩硬件问题
charge failed ~-~ 充电失败
charge failed. Out of time: {1} ~-~ 充电失败。超出时间: {1}
{1} is set. Out of waiting time: {2} ~-~ {1} 已设置。超出等待时间: {2}
charge timeout: {1} ~-~ 充电超时: {1}
GoPathDi init model is null ~-~ GoPathDi 初始化模型为空
DI TRUE BUT AWAY GOAL DIST: {1} ~-~ DI 已触发，但与目标距离为: {1}
GoPathJackDi init model is null ~-~ GoPathJackDi 初始化模型为空
GoZPath init model is null ~-~ GoZPath 初始化模型为空
zpath task parameter error:{1} ~-~ Z 型路径任务参数错误:{1}
Can't open Recfile, while Hook. File: {1} ~-~ 牵引时无法打开识别文件。文件: {1}
m_clampReachDI: {1} doesn't exits. ~-~ m_clampReachDI: {1} 不存在。
m_releaseReachDI {1} doesn't exits. ~-~ m_releaseReachDI {1} 不存在。
Hook init model is null ~-~ Hook  初始化模型为空
Doesn't support hook type: {1} ~-~ 不支持牵引类型: {1}
Hook has Goods. Cannot Clamp! ~-~ 挂钩上有货物。无法夹紧!
Clamp Time Out! ~-~ 夹紧超时!
Release Hook Time Out! ~-~ 释放挂钩超时!
Jack init model is null ~-~ 顶升初始化模型为空
Jack module's Motors are empty! ~-~ 顶升模块的电机为空!
Can't open Recfile, while Jack. File: {1} ~-~ 顶升时无法打开识别文件。文件: {1}
Action Over Time {1} ~-~ 动作超时 {1}
Can't open Recfile, while customJack. File: {1} ~-~ 自定义顶升时无法打开识别文件。文件: {1}
JackCustom init model is null ~-~ JackCustom 初始化模型为空
KeepStop init model is null ~-~ KeepStop 初始化模型为空
Can't open Recfile, while ModbusJack. File: {1} ~-~ Modbus 顶升时无法打开识别文件。文件: {1}
ModbusJack init model is null ~-~ ModbusJack 初始化模型为空
Error jack cmd ~-~ 顶升命令错误
connection error ~-~ 连接错误
unknow jack error ~-~ 未知顶升错误
Can't open Recfile, while ModbusTractor. File: {1} ~-~ ModbusTractor 无法打开识别文件。文件: {1}
ModbusTractor init model is null ~-~ ModbusTractor 初始化模型为空
ModbusTractor error: {1} ~-~ ModbusTractor 错误：{1}
counterPoint DI can't keep triggered for {1} ms ~-~ counterPoint DI 无法保持触发 {1} 毫秒
jack counter pointer over time error ~-~ 顶升计数器指针超时错误
jack connection error ~-~ 顶升连接错误
unknown jack error ~-~ 未知顶升错误
jack connection error. ~-~ 顶升连接错误。
Motor init model is null ~-~ 电机初始化模型为空
stopDI :{1} is not in the robot.model ~-~ stopDI :{1} 不在机器人模型中
no motor or wrong command ~-~ 没有电机或错误的命令
no motor param ~-~ 没有电机参数
motor param is none ~-~ 电机参数为空
{1} isn't in odo message! ~-~ {1} 不在里程计消息中!
Reach downLimit!!! Di {1} ~-~ 达到下限位!!! Di {1}
Reach upLimit!!! Di {1} ~-~ 达到上限位!!! Di {1}
{1} {2} bypass zero di. Please zero Motor ~-~ {1} {2} 绕过标零 DI。请将电机标零
{1} {2} larger than motor.maxValue: {3} ~-~ {1} {2} 大于电机最大值: {3}
{1} {2} smaller than motor.minValue: {3} ~-~ {1} {2} 小于电机最小值: {3}
{1} type doesn't support!!! ~-~ {1} 类型不支持!!!
OpenBlinkDO init model is null ~-~ OpenBlinkDO 初始化模型为空
Cannot open blinkDO: {1} ~-~ 无法打开 blinkDO: {1}
OpenDO init model is null ~-~ OpenDO 初始化模型为空
DO {1} is not in the robot model ~-~ DO {1} 不在机器人模型中
PlanForkPath init model is null ~-~ PlanForkPath 初始化模型为空
PlanPath init model is null ~-~ PlanPath 初始化模型为空
PushPositive init model is null ~-~ PushPositive 初始化模型为空
pushMotor is empty! ~-~ 推动电机为空!
PutBattery init model is null ~-~ PutBattery 初始化模型为空
rec fail reach max times: {1} ~-~ 记录失败达到最大次数: {1}
adjust fail reach max times: {1} ~-~ 调整失败达到最大次数: {1}
Cannot Recognize Battery! ~-~ 无法识别电池!
recognition result is invalid {1} ~-~ 识别结果无效 {1}
Can't read Recfile. File: {1} {2} {3} {4} {5} {6} {7} ~-~ 无法读取识别文件。文件: {1} {2} {3} {4} {5} {6} {7}
GoPathDi init model is null ~-~ GoPathDi 初始化模型为空
Fork Pointer in QuickGo is null ~-~ QuickGo 中的叉车指针为空
RecAdjustYTheta init model is null ~-~ RecAdjustYTheta 初始化模型为空
rec fail reach max times: {1} ~-~ 记录失败达到最大次数: {1}
The target angle is too large. {1} {2} ~-~ 目标角度太大。{1} {2}
The adjust dist is too small. {1} ~-~ 调整距离太小。{1}
recognition result is invalid {1} ~-~ 识别结果无效 {1}
RecAndGoPathDi init model is null ~-~ RecAndGoPathDi 初始化模型为空
RecCharge init model is null ~-~ RecCharge 始化模型为空
charge timeout: {1} in rec stage. ~-~ 识别阶段充电超时: {1}。
Charge device is not enable! ~-~ 充电设备未启用!
can not open Recfile.{1} ~-~ 无法打开识别文件.{1}
recognize charger failed ~-~ 识别充电桩失败
charger's recognition result is invalid {1} ~-~ 充电桩的识别结果无效 {1}
more than one charger recognized ~-~ 识别出多个充电桩
no charger recognized ~-~ 未识别出充电桩
RecGo init model is null ~-~ RecGo 初始化模型为空
RecInitHeight init model is null ~-~ RecInitHeight 初始化模型为空
cannot detect goods height! reach max height {1}. ~-~ 无法检测到货物高度! 达到最大高度 {1}。
BackLaser's laser_id {1} is not in the laser devices ~-~ 后激光的激光 id {1} 不在激光设备中
BackLaser is being blocked. Please reset fork start_height. ~-~ 后激光被阻挡。请重置叉车起始高度。
RecQRCode init model is null ~-~ RecQRCode 初始化模型为空
rec fail reach max times: {1} ~-~ 识别失败达到最大次数: {1}
The pallet or tag is out of the right poistion. ~-~ 托盘或标签位置不正确。
Cannot Recognize QRCode! ~-~ 无法识别二维码!
recognition result is invalid ~-~ 识别结果无效
Layer num is {1} Rec layers number is {2} ~-~ 层数是 {1} 记录层数是 {2}
Can't open Recfile. Recfile is empty. ~-~ 无法打开识别文件。识别文件为空。
Can't open Recfile. File name is "{1}"~-~ 无法打开识别文件。文件名是"{1}"
RecShelf init model is null ~-~ RecShelf 初始化模型为空
The Goal has goods. ~-~ 目标有货物。
The Goal doesn't have goods. Cannot Load ~-~ 目标没有货物。无法取货
Cannot Unload. There are objects in target pos. ~-~ 无法放货。目标位置有货物。
Can't open Recfile, while RecShelf. File: {1} ~-~ 识别货架时无法打开识别文件。文件：{1}
has not recognized a shelf, return false ~-~ 未识别出货架，返回假
shelf position is too far away.{1} ~-~ 货架位置太远。{1}
shelf result unvalid return ~-~ 货架结果无效返回
more than one shelf pose recognized. ~-~ 识别出多个货架姿态。
RestartClean init model is null ~-~ RestartClean 初始化模型为空
The robot is not in the cleaning area ~-~ 机器人不在清洁区域
Roller init model is null ~-~ Roller 初始化模型为空
Roller error: {1}, state: {2}, emc: {3}, enable: {4} ~-~ 辊筒错误: {1}, 状态: {2}, emc: {3}, 启用: {4}
roller operation error ~-~ 辊筒操作错误
Cannot Recognize QRCode! ~-~ 无法识别二维码！
the {1}th recognition result is invalid {2} ~-~ 第 {1} 个识别结果无效 {2}
rec results is empty! ~-~ 识别结果为空!
DO {1} is not in the robot model ~-~ DO {1} 不在机器人模型中
RunScript init model is null ~-~ RunScript 初始化模型为空
script_args error! {1} ~-~ 脚本参数错误! {1}
no script name ~-~ 没有脚本名称
robot is blocked in script mode ~-~ 机器人在脚本模式中被阻塞
Input wrong rec result index. ~-~ 输入错误的识别结果索引。
User error code is 53800~53899 User warning code is 55800~55899 ~-~ 用户错误代码是 53800~53899 用户警告代码是 55800~55899
convert moveTask error: {1} ~-~ 转换移动任务错误: {1}
Script model not init! ~-~ 脚本模型未初始化!
SecondAdj init model is null ~-~ SecondAdj 初始化模型为空
The target angle is too large. {1} {2} ~-~ 目标角度太大。{1} {2}
The adjust dist is too small. {1} ~-~ 调整距离太小。{1}
adjust reaches max times. {1} ~-~ 调整达到最大次数。{1}
Sound init model is null ~-~ Sound 初始化模型为空
SpinAction init model is null ~-~ SpinAction 初始化模型为空
PGV cannot find code. Maybe the shelf is moved. Please adjust the shelf's position ~-~ PGV找不到二维码。可能是货架移动了。请调整货架位置
PGV cannot find code over time. The robot is stopped. ~-~ PGV在规定时间内找不到二维码。机器人已停止。
Shelf is outside the safe region. dx = {1} dy = {2} ds = {3} dtheta = {4} ~-~ 货架在安全区域外。dx = {1} dy = {2} ds = {3} dtheta = {4}
The angle of Shelf is outside the safe region. dtheta = {1} ~-~ 货架的角度在安全区域外。dtheta = {1}
Shelf has system error sum_e {1} ~-~ 货架有系统错误 sum_e {1}
Cannot Find Spin Motor: {1} ~-~ 找不到旋转电机: {1}
Caution: robot is blocked ~-~ 注意: 机器人被阻挡
StopClean init model is null ~-~ StopClean 初始化模型为空
The robot is not in the cleaning area ~-~ 机器人不在清洁区域
waitDI init model is null ~-~waitDI 初始化模型为空
Di {1} is not in the robot model ~-~ Di {1} 不在机器人模型中
Di {1} is false. WaitDI stable {2}s ~-~ Di {1} 为关。等待 DI 稳定 {2} 秒
Task is failed by EMC/trigger/external. ~-~ 任务因EMC/触发器/外部失败
has same id number! ~-~ 有相同的 ID 号码!
parse error in vda5050: {1}.{2} ~-~ vda5050 解析错误: {1}.{2}
{1} model has not been actived, please contact SEER to active this model ~-~ {1} 模型尚未激活，请与SEER联系激活此模型
dualDiff module doesn't have all walk motors! ~-~ 双差速模组没有所有的行走电机!
{1} value is missing or wrong !{2} ~-~ {1} 值缺失或错误!{2}
method is not forward or backward !{1} ~-~ 方法不是前进或后退 !{1}
percentage is [0,1] !{1} ~-~ 百分比是在 [0,1] !{1}
parse error in script_args: {1}.{2} ~-~ 脚本参数解析错误: {1}.{2}
parse error in {1} {2}.{3} ~-~ 解析错误在 {1} {2}.{3}
parse error in dispatcherArgs: {1}.{2} ~-~ 分派参数解析错误: {1}.{2}
parse error in armArgs: {1}.{2} ~-~ 手臂参数解析错误: {1}.{2}
Doesn't support key: {1} {2} ~-~ 不支持键: {1} {2}
label: {1} is not in the map ~-~ 标签: {1} 不在地图中
source_label: {1} is not in the map ~-~ 源标签: {1} 不在地图中
BinTask: {1} is not in the {2}. The binTask are ~-~ BinTask: {1} 不在 {2} 中。Bin任务是
preBinTask: {1} is not in the {2}. The binTask are ~-~ preBinTask: {1} 不在 {2} 中。Bin任务是
parse error in body : {1} ~-~ 主体中的解析错误: {1}
Failed to initialize mobilerobots: {1} ~-~ 初始化移动机器人失败: {1}
Fail to open {1} ~-~ 打开失败 {1}
Cannot in AutoMode Without Location ~-~ 无法在没有定位的情况下进入自动模式
Do not find path to {1} ~-~ 未找到通往 {1} 的路径
Forbidden direct goto. Do not find path to {1} ~-~ 禁止直接跳转。未找到通往 {1} 的路径
There is a loop in prepoints! ~-~ prepoints 中存在循环!
can not find target id {1} ~-~ 找不到目标ID {1}
Movetasklist is not array: {1} ~-~ 移动任务列表不是数组: {1}
Parse movetask fail: {1} ~-~ 解析移动任务失败: {1}
Parse movetasklist fail: {1} ~-~ 解析移动任务列表失败: {1}
move_task_list size is zero! ~-~ 移动任务列表大小为零!
task pool size is not equal to edge_lists size ~-~ 任务池大小不等于边列表大小
Path planning failed. Cannot find Path between: {1},{2} ~-~ 路径规划失败。无法找到路径在: {1},{2} 之间
3066 Robot sending task error, cur_source_name = {1}, last_target_name = {2}, last_percentage = {3} ~-~ 3066 机器人发送任务错误，当前起点名称 = {1}, 上一次目标名称 = {2}, 上一次线路百分比 = {3}
path percentage is smaller than previous one. cur_percentage: {1} {2} {3} ~-~ 路径百分比小于前一个。当前百分比: {1} {2} {3}
Cannot goto same point {1} in rec mode. Please goto other points first! ~-~ 无法在识别模式下前往同一点 {1}。请先前往其他点!
polygon ~-~ 多边形
Slow up height of recInitHeight function ~-~ 减慢recInitHeight函数的高度
fork tail laser id ~-~ 叉车尾部激光 ID
back laser rec angle. ~-~ 后置激光识别角度
Max extra fork down distance with ultrasonic Di ~-~ 超声波 DI 额外最大货叉下降距离
Open the steer motor following error monitor ~-~ 打开舵轮电机跟随错误监控
Time threshold of the duration of steer motor following error ~-~ 转向电机跟随错误持续时间的时间阈值
GoodsId isn't same. Detected goodsId is {1}. Sended goodsId is {2}. ~-~ GoodsId 不一致。检测到的 GoodsId 是 {1}。发送的 GoodsId 是 {2}
Critical speed for phase change when unloaded ~-~ 放货时相变的关键速度
Critical speed for phase change when loaded ~-~ 载货时相变的关键速度
JMaximum rotational acceleration Jerk(°/s^3) ~-~ 最大旋转减加速度Jerk(～/s^3)
Free navigation path replace quality threshold ~-~ 自由导航路径替换质量阈值
Free navigation max rotation speed (°) ~-~ 自由导航最大旋转速度 (°)
Whether to relax safety constraints to meet kinematic constraints ~-~ 是否放宽安全约束以满足运动学约束
Free navigation loacl planning start distance (m) ~-~ 自由导航本地规划开始距离 (m)
The AGV is in the extern control mode! ~-~ AGV处于外部控制模式!
ManualBlock is False. ~-~ 手动阻塞为假。
Ignoring Task caused by DISensor {1} ~-~ 忽略由 DI 传感器 {1} 引起的任务
{1} checkDi is false. Di: ~-~ {1} checkDi 为假。Di:
robot is slipping.slip.vx.t = {1}, slip.vx.v = {2} ~-~ 机器人打滑。滑移速度时间 = {1}, 滑移速度 = {2}
robot is slipping. slip.vw.t = {1}, slip.vw.v = {2} ~-~ 机器人打滑。角度滑移时间 = {1}, 滑移角速度 = {2}
robot is waiting for reply, reply task_id should be {1} ~-~ 机器人正在等待回复，回复任务ID应该是 {1}
Steer motor following error. ~-~ 舵轮电机跟随错误。
cannot find motor in navSpeed message: {1} ~-~ 在导航速度消息中找不到电机: {1}
walk motor number is not 2 or 4!!!{1} ~-~ 行走电机数量不是2或4!!!{1}
target x is null ~-~ 目标 X 为空
target y is null ~-~ 目标 Y 为空
target theta is null ~-~ 目标角度为空
target is null ~-~ 目标为空
circle radius is null ~-~ 圆半径为空
circle x is null ~-~ 圆 X 为空
circle y is null ~-~ 圆 Y 为空
circle is null ~-~ 圆为空
robot is outside the circle. ~-~ 机器人在圆外。
Can not find collision path!!! ~-~ 找不到碰撞路径!!!
Please use only rotate function. Current cannot support zero rot_radius! ~-~ 请只使用旋转功能。当前不支持零旋转半径!
lack of params: {1} {2} {3} ~-~ 缺少参数: {1} {2} {3}
Cannot locate the shelf! ~-~ 无法定位货架!
Cannot locate the shelf again! ~-~ 无法再次定位货架!
robot out of path : {1} {2} ~-~ 机器人偏离路径 : {1} {2}
Dosn't Support Go With Spin and Avoid Obs! ~-~ 不支持旋转并避免障碍物!
Caution: robot is outside path ~-~ 注意: 机器人在路径外
path planning over {1}s ~-~ 路径规划超过 {1} 秒
motion plan failed! ~-~ 运动规划失败!
Accuracy error is too large(xy): {1} ~-~ 精度误差过大(xy): {1}
Accuracy error is too large(angle): {1} ~-~ 精度误差过大(角度): {1}
cannot find motor in odo message: {1} ~-~ 在里程计消息中找不到电机: {1}
cannot find motor in navSpeed message: {1} ~-~ 在导航速度消息中找不到电机: {1}
{1} steer Range {2} {3} ~-~ {1} 舵轮范围 {2} {3}
Steer: {1} isn't in the robot.model. ~-~ 舵轮: {1} 不在机器人模型中。
Dosn't Support Go With Spin and Avoid Obs! ~-~ 不支持随动并避障!
path planning over {1}s ~-~ 路径规划超过 {1} 秒
m_planner fails in MultiSteers LocalGoto ~-~ m_planner在多舵轮 LocalGoto 中失败
m_planner is NULL in MultiSteers LocalGoto ~-~ m_planner在多舵轮 LocalGoto 中为空
AGV cannot support self rotate. Please redraw the path or close the CheckSelfRotateError! ~-~AGV不支持自旋转。请重新绘制路径或关闭CheckSelfRotateError!
motion plan failed! ~-~ 运动规划失败!
Please use only rotate function. Current cannot support zero rot_radius! ~-~ 请只使用旋转功能。当前不支持零旋转半径!
The number of steers is smaller than 2!{1} ~-~ 转向数量少于2!{1}
The number of walk motor larger than the number of steer motor!{1} {2} ~-~ 行走电机的数量大于转向电机的数量!{1} {2}
The position of {1} doesn't match postion in the steer motors ~-~ {1} 的位置与转向电机中的位置不匹配
cannot find chassisDistanceSensor or liftDistanceName in publish message: ~-~ 在发布消息中找不到底盘距离传感器或升降距离名称:
vy: {1} lift_dist: {2} liftBottom: {3} ~-~ vy: {1} 升降距离: {2} 升降底部: {3}
CANNOT AVOID GO WITH CHARGING ~-~ 充电时无法避障
Can not find collision path!!! ~-~ 找不到碰撞路径!!!
GoWithReStart init error! ~-~ GoWithReStart 初始化错误!
GoWithReStart error! ~-~ GoWithReStart 错误!
robot out of path : {1} {2} ~-~ 机器人偏离路径 : {1} {2}
walk motor number is not 1!!!{1} ~-~ 行走电机数量不是1!!!{1}
steer motor number is not 1!!!{1} ~-~ 转向电机数量不是1!!!{1}
steer motor number is empty !!! ~-~ 转向电机数量为空!!!
walk motor number is empty !!! ~-~ 行走电机数量为空!!!
L = {1} is too small ! ~-~ L = {1} 太小了!
fork is charging, cannot manual control ~-~ 叉车正在充电，无法手动控制
The bias between the current fork height and the target value is too much. Fork target height: {1}. Current fork height: {2}. ~-~ 当前货叉高度与目标值之间的偏差过大。货叉目标高度: {1}。当前货叉高度: {2}.
Selected odometer FAILED to initialize ~-~ 选定的里程计初始化失败
Selected odometer initialized ~-~ 选定的里程计已初始化
Following error monitor FAILED to initialize ~-~ 跟随错误监控初始化失败
Odometer FAILED to update using the Message_MotorInfos ~-~ 里程计未能使用 Message_MotorInfos 更新
Motor following error monitor FAILED to update using the Message_MotorInfos ~-~ 电机跟随错误监控未能使用 Message_MotorInfos 更新
Motor following error monitor FAILED to update using the Message_NavSpeed ~-~ 电机跟随错误监控未能使用 Message_NavSpeed 更新
The angle at which the overturning alarm is triggered(deg) ~-~ 倾覆报警触发的角度(度)
Is the overturning alarm activated ~-~ 倾覆报警是否被激活
beam_index beyond border. beam_index = {1}. now_drop = {2}. user_data.size() = {3}. i = {4}. ScanUsedNum.get() = {5} ~-~ 光束索引超出边界。光束索引 = {1}。当前下降 = {2}。用户数据大小 = {3}。i = {4}。ScanUsedNum.get() = {5}
unknow depth camera: {1}. We set id to 0 ~-~ 未知深度相机: {1}。我们将ID设置为0
3D camera : cannot receive trigger data ~-~ 3D 相机 ： 未收到触发数据
Deep learning mode is loading, please recognize it later ~-~ 深度学习模型加载中，请稍后重新识别

Auto Relocation Gird Size ~-~ 自动位置重定位网格大小
Use Laser Undistortion ~-~ 使用激光去畸变
Use mid360 for localization ~-~ 使用mid360进行定位
enable skid correction ~-~ 启用打滑校正
The effective length of reflector length ~-~ 反射器长度的有效长度
The make up for reflectors center / m ~-~ 反射器中心的补偿值 / 米
whether to use particle filter optimization ~-~ 是否使用粒子滤波优化
All Motors are empty! ~-~ 所有电机都是空的！
operation error!!! ~-~ 操作错误！！！
Cannot Recognize {1}. ~-~ 无法识别{1}。
Cannot Recognize! ~-~ 无法识别！
source_id is empty !!!{1} ~-~ source_id为空！！！{1}
Whether to hold direction for Omnidirectional robot in free navigation ~-~ 在自由导航中是否保持全向机器人的方向
DI{1}, ~-~ DI{1}，
forbidden. ~-~ 禁止。
robot is slippling ~-~ 机器人打滑了
repeatedly. ~-~ 反复发生。
slip.vx.t = {1}, slip.vx.v = {2} slip.vw.t = {3}, slip.vw.v = {4} ~-~ slip.vx.t = {1}，slip.vx.v = {2} slip.vw.t = {3}，slip.vw.v = {4}
{1} steer Range: {2} {3} ~-~ {1}转向范围：{2} {3}
Fail action cannot find shelf ~-~ 失败操作无法找到货架
walk motor number is not 4 and not 8!!!{1} ~-~ 步进电机数量不是4也不是8！！！{1}
cannot find motor in odo message: {1} {2} ~-~ 在odo消息中找不到电机：{1} {2}
cannot find motor in navSpeed message: {1} {2} ~-~ 在navSpeed消息中找不到电机：{1} {2}
path planning over {1} s ~-~ 路径规划超过{1}秒
steer Range: {1} {2} ~-~ 转向范围：{1} {2}
Visio Scan RD : real step is different with default step ,default step is : 0.33 ,real step is : ~-~ 视觉扫描RD：实际步长与默认步长不同，默认步长为：0.33，实际步长为：
OM time to record after stop ~-~ 停止后记录OM时间
goods exceed the pallet {1} m, recognize fail ! ~-~ 货物超过{1}米的托盘，识别失败！
Recofile not exist!!!! ~-~ Reco文件不存在！！！
get some shapes, but not fit ,please check saved pics!!!! ~-~ 获取了一些形状，但不合适，请检查保存的图片！！！
distance Beyond Pallet,0 is not do detect ~-~ 超出托盘距离，无法检测0
recognize form file: file load error ~-~ 从文件中识别：文件加载错误
sensor fusion data debugging type. 0: local 1: global 2: all ~-~ 传感器融合数据调试类型。0：本地1：全局2：全部
AGV cannot support rotate. Please redraw the path or close the CheckSelfRotateError! ~-~ AGV不能支持旋转。请重新绘制路径或关闭CheckSelfRotateError！
motorName, nly motor can be enabled(conflict with EMC driver protocol EMC) ~-~ motorName，只有电机可以启用（与EMC驱动程序协议EMC冲突）
motorName, nly motor can be disabled(conflict with EMC driver protocol EMC) ~-~ motorName，只有电机可以禁用（与EMC驱动程序协议EMC冲突）
Wait too long for the input data ~-~ 等待输入数据时间过长
FAILED to parsethe input data ~-~ 无法解析输入数据
Bi-steer mean offset calibration section finished ~-~ 双转向平均偏移校准部分完成
Unexpected state in mean steer offset calibration ~-~ 平均转向偏移校准中出现意外状态
FAILED to generate results ~-~ 无法生成结果
Bi-steer mean offset calibration results generated ~-~ 生成了双转向平均偏移校准结果
Clear the .cp values for steer motors ~-~ 清除转向电机的.cp值
Create virtual devices in model file ~-~ 在模型文件中创建虚拟设备
Unexpected CalibMoveType ~-~ 意外的CalibMoveType
Update params because .cp file changed ~-~ 更新参数，因为.cp文件已更改
Update params because model file changed ~-~ 更新参数，因为模型文件已更改
ABORTED because {1}[{2}] ({3}) obstructs calibration ~-~ 中止，因为{1}[{2}] ({3})阻碍了校准
Key 'data' is MISSING in the parsed results ~-~ 解析结果中缺少键'data'
Call service RecoFactory::getCalibRes({1}, true ~-~ 调用RecoFactory::getCalibRes({1}, true)服务
Clear steerOffset data file name in .cp file for steer motor {1} ~-~ 在.cp文件中清除转向电机{1}的steerOffset数据文件名
Clear the .cp values for {1} ~-~ 清除{1}的.cp值
Steering to {1} ~-~ 转向至{1}
FAILED to steer to {1} ~-~ 转向至{1}失败
Steered to {1} ~-~ 已转向至{1}
Data section is recorded with index ( {1}, {2} ) ~-~ 数据部分已记录索引（{1}，{2}）
NOT all wheel speed samples were collected! Sampling FAILED at the speed: {1} ~-~ 并非所有车轮速度样本都被收集！在速度{1}时采样失败
Repeated laser-odom calibration results generated with movement {1} ~-~ 重复的激光-里程计校准结果生成，移动{1}
Temporal steer offset calibration displacement (m): {1} ~-~ 时间转向偏移校准位移（米）：{1}
Temporal steer offset calibration rotation (deg): {1} ~-~ 时间转向偏移校准旋转角度（度）：{1}
FAILED to parse the input data ~-~ 无法解析输入数据
Clear the .cp values for {1} ~-~ 清除{1}的.cp值
estimate laser yaw bias ~-~ 估计雷达 yaw 角外参的偏置信息
open interpolate localization ~-~ 打开插值器融合模块
time delay step ~-~ 时间延迟步长
detectBinShape ~-~ 检测库位形状
measure result has shown goods's edge has exceed pallet width ~-~ 测量结果显示货物超出了栈板宽度方向
No pointCloud in current detection area: X_min: {1}  X_max: {2}  Y_min:{3}   Y_max:{4}  Z_min:{5}  Z_max:{6} ~-~  识别相机中,当前区域没有栈板, 识别区域 X_min: {1}  X_max: {2}  Y_min:{3}   Y_max:{4}  Z_min:{5}  Z_max:{6}
Goods is on the fork arms! ~-~ 货物在货叉上被带动！
odo_move ptr is null! ~-~ 里程移动指针为 null
Recovery(s) will start after being blocked (s) ~-~ 被阻挡后开始恢复的间隔时间(s)
WKp value of line patrol PID in mag navigation ~-~ 磁导航巡线 PID 的 wKp 值
WKd value of line patrol PID in mag navigation ~-~ 磁导航巡线 PID 的 wKd 值
Steer Kp value of differential module car ~-~ 差速模组车的舵轮 Kp 值
steer Kd value of differential module car ~-~ 差速模组车的舵轮 Kd 值
minimum rudder angle resolution (degrees)) ~-~ 最小舵角分辨率(degrees)
charger in manual mode ~-~ 充电桩在手动控制模式
Enable or disable logger monitoring. Take effect after restart. ~-~ 启用或禁用日志监控，重启后生效
odom data lags behind the imu by approximately(ms)：{1} ~-~ 里程比IMU滞后(ms)：{1}
imu data lags behind the odom. imu:{1} odom:{2} ~-~ IMU比里程滞后(ms)：imu:{1} odom:{2}
no 3d map ~-~ 没有3D地图
Hardware capability does not support stacker forklifts. ~-~  硬件能力不支持堆高叉车
Hardware capability does not support more than 2 steering wheels. ~-~ 硬件能力不支持舵轮数量大于2
Hardware capability does not support the differential module. ~-~ 硬件能力不支持差速模组
Hardware capability does not support Mecanum wheels. ~-~ 硬件能力不支持麦克拉姆轮
Hardware capability does not support an Ackermann chassis. ~-~ 硬件能力不支持阿克曼底盘
Whether to clear msg after getmsg ~-~ 
Angule in PGV calibration (deg) ~-~ 
The motor wheelRadius is too small ~-~ 
GenenalCam-Odom abort for not in 3D localization method ~-~ 
Data number not right ~-~ 
Cleaer the .cp values for {1} ~-~ 
ABORTED because no Laser use for localization ~-~ 
special log config parameters ~-~ 
log exchange msg or not ~-~ 
log post msg or not ~-~ 
log msg from rbk or not ~-~ 
log CodesysCommand msg detiles from Codesys Runtime or not ~-~ 
log CodesysCommand response msg detiles from Codesys Runtime or not ~-~ 
log MotorInfos msg detiles from Codesys Runtime or not ~-~ 
Stack ~-~ 
control chassis via controller directly ~-~ 
control chassis via PLC with SEER-TCP stack ~-~ 
enable to log socket frames ~-~ 
fast exchange msg period ~-~ 
standard exchange msg period ~-~ 
StartSaveCanLog ~-~ 
StopSaveCanLog ~-~ 
DOMotor Limit Triggered: ~-~ 
LanHai-LDSx-485 ~-~ 
ReagleSensing-485 ~-~ 
PLD_485 ~-~ 
JuqiangDistanceSensor ~-~ 
canport ~-~ 
Charging voltage ~-~ 
电池允许的最大充电电压 ~-~ 
ChargingMode ~-~ 
协议充电 ~-~ 
状态充电 ~-~ 
电池总容量 ~-~ 
大小恒流切换阈值 ~-~ 
大恒流 ~-~ 
小恒流 ~-~ 
stdio id ~-~ 
stdio communication channel ~-~ 
 ~-~ 
bindDi ~-~ 
startDi ~-~ 
speedLimit ~-~ 
ossdEnable ~-~ 
disable ~-~ 
enable ~-~ 
pluse cycle ~-~ 
pulse width ~-~ 
check timeout ~-~ 
inverse ~-~ 
velocityLimit ~-~ 
mutingDo ~-~ 
stoDoPair ~-~ 
sbcDoPair ~-~ 
json ~-~ 
SLS ~-~ 
SSM ~-~ 
xml ~-~ 
SafeModule Error, watchdog reset! ~-~ 
expansion coeff of cal encoder max diff ~-~ 
Motor ignore Navspeed in Slowdown ~-~ 
SeerPGV not activated ~-~ 
TABOS-None-Private ~-~ 
Quick equipment stop ~-~ 
Curtis-F2A-ZhongLi ~-~ 
Inovance-CanOpen ~-~ 
out Encoder Single-Trun Resolution Ratio bit ~-~ 
out Encoder Multi-Trun Resolution Ratio bit ~-~ 
CodesysMotor ~-~ 
this motor controled by RBK or Codesys User ~-~ 
Using the Code Tape Mode ~-~ 
Seer SLM-CPD0812 ~-~ 
use g2o ~-~ 
check angle distribution ~-~ 
feature loc enable ~-~ 
weather use odom for feature loc ~-~ 
weather need shock detection for feature loc ~-~ 
weather consider dir of lines for feature loc ~-~ 
valid range of feature loc ~-~ 
degradation thd of feature loc ~-~ 
rotate thd of feature loc ~-~ 
score thd of feature loc ~-~ 
min match size of feature loc ~-~ 
max iter times of feature loc ~-~ 
match err thd of feature loc ~-~ 
map update enable ~-~ 
Save new feature map ~-~ 
the range of map update ~-~ 
the remove thd of lines ~-~ 
enable point to plane reloc ~-~ 
distance cannot see the tag report error ~-~ 
distance cannot see the tag report warning ~-~ 
visualize cur line ~-~ 
dynamic load likelihood map ~-~ 
visualize submap ~-~ 
submap expend range ~-~ 
cannot detect tag after short distance ~-~ 
cannot detect tag after long distance ~-~ 
device ID ~-~ 
distance between magneticpoints ~-~ 
number of magnetic points ~-~ 
DoWayTech ~-~ 
communication interface type ~-~ 
baud for rs485 ~-~ 
magnetic log freq ~-~ 
debug for magnetic ~-~ 
MagneticSensor init failed! ~-~ 
MagneticSensor send Init failed ~-~ 
MagneticSensor update timeout ~-~ 
ChargeOpenSpeed init model is null ~-~ 
LiveGoPathDi init model is null ~-~ 
rec result invalid. tacker_id = ~-~ 
cannot find rec result. tacker_id = ~-~ 
cannot find rec result in ~-~ 
robot is waiting for planning. ~-~ 
pgv ptr is null! ~-~ 
fork_height ptr is null! ~-~ 
TcpPlan init model is null ~-~ 
model name is wrong ~-~ 
{1} need a string value. Get {2} ~-~ 
horizon motor name ~-~ 
vertical sensor name ~-~ 
The angle between the vertical track and the horizontal track. ~-~ 
veclocity vector mode ~-~ 
module parameters ~-~ 
delay arrive time ~-~ 
back laser detection width. ~-~ 
max integrate speed ~-~ 
the ratio between robot rot and spin motor ~-~ 
wifi mesh config for esp32 ~-~ 
3066 Robot sending task error, cur_source_name = {1}, cur_task_id = {2}, last_target_name = {3}, last_task_id = {4} ~-~ 
The robot is charging. Please wait until it disconnects from the charging station. ~-~ 
Max Speed (m/s) ~-~ 
Use mpc mode to follow ~-~ 
Max Back Speed (m/s) ~-~ 
Adjust goods direction ~-~ 
Spin zero nearby parallel ~-~ 
S-Curve Speed Profile ~-~ 
0-OFF,1-WIFI,2-ESP Distribution mode for multi robot navigation ~-~ 
Local map print for debug ~-~ 
Local map inflation radius (m) ~-~ 
Local map lethal radius (m) ~-~ 
Local map infation cost decay factor ~-~ 
Free navigation theta star search cost ~-~ 
Free navigation theta star ref path hcost weight ~-~ 
Free navigation avoid obstacle first rather than follow path ~-~ 
Free navigation alaways replan local path even if old path is passable ~-~ 
Free navigation using dwa method ~-~ 
tuning inflate by speed ~-~ 
slow down when near obs or curve path ~-~ 
DWA obs cost scale ~-~ 
DWA path cost scale ~-~ 
DWA goal cost scale ~-~ 
DWA obstacle collision check mode ~-~ 
DWA path score mode ~-~ 
DWA look ahead dist on path ~-~ 
DWA path score linear weight ~-~ 
DWA path score align weight ~-~ 
DWA goal mode ~-~ 
DWA vel cost scale ~-~ 
DWA traj sim time ~-~ 
DWA precise reach, which may cause shaking at goal ~-~ 
DWA find backup goal when nav goal is blocked ~-~ 
Whether enable recovery ~-~ 
Free navigation reach distance when robot blocked for target has obstacle ~-~ 
convex path plan ~-~ 
Hardware capability does not support Ackermann steering. ~-~ 
Steer motor following error.{1} ~-~ 
DWA is empty! ~-~ 
robot in recovery ~-~ 
walk motor number is invalid ~-~ 
magnetic {1} mag_res {2} doesn't match value size {3} ~-~ 
The position x of magnetic is wrong! ~-~ 
invalid diff steers number ~-~ 
walk motor number is less than 3 ~-~ 
walk motor number is less than 3. {1} ~-~ 
The vKp value ~-~ 
The vKd value ~-~ 
The wKp value ~-~ 
The wKd value ~-~ 
The x value of the VV car LQR, the larger the following effect, the better, but the jitter will also increase ~-~ 
The y value of the VV car LQR, the larger the follow-up effect, the better the jitter ~-~ 
The theta value of the LQR of a VV car, the larger the follow-up effect, the better the jitter ~-~ 
pro_rec_func - has not been actived, please contact SEER to active this function ~-~ 
hole point number ~-~ 
hole radius ~-~ 
cannot init Dahua ~-~ 
cannot set auto exposure from Dahua ~-~ 
cannot set exposure time from Dahua ~-~ 
3D camera : set depth to rgb fault for Lanxin ~-~ 
config camera ~-~ 
can't receive percip data ~-~ 
SeerPGV timeout: ~-~ 
PgvCamera, can't get the channel_name ~-~ 
SeerPGV not activated: ~-~ 
PgvCamera, func invalid, only support adjust, localization or adjustLocalization: ~-~ 
cannot receive laser data from pacecat m300, ip: ~-~ 
cannot receive Visioscan RD data , from ~-~ 
cannot init Visioscan RD , from ~-~ 
identity ratio ~-~ 
cannot connect to laser, because the laser type is not supported : ~-~ 
ShadowMinAngle ~-~ 
Filtering
  // parameters ~-~ 
ShadowMaxAngle ~-~ 
ShadowWindow ~-~ 
ShadowNeighbours ~-~ 
Hinson cannot Init driver, from ip : ~-~ 
cannot Init driver, from ip : ~-~ 
LS_N301_V1_7 : laser lost connect , from : ~-~ 
and port : ~-~ 
convert laser data failed ~-~ 
cannot convert laser data ~-~ 
timeout receive laser data from Nanosick, IP: ~-~ 
please restart laser, get internal Error with Nanosick, IP: ~-~ 
please clean laser, get Contamination Error with Nanosick, IP: ~-~ 
timeout receive laser data from olam, IP: ~-~ 
cannot Init Hinson SE1035 driver ~-~ 
keli_KLMS laser cannot receive data with Compact data type!!! from ~-~ 
Maximum speed that can be modified by controller (m/s) ~-~ 
Minimum speed that can be modified by controller (m/s) ~-~ 
Current speed when controlled by controller (m/s) ~-~ 
Maximum speed of fork that can be modified by controller (m/s) ~-~ 
Minimum speed of fork that can be modified by controller (m/s) ~-~ 
Current speed of fork when controlled by controller (m/s) ~-~ 
Maximum rotation speed can be modified by controller (°/s) ~-~ 
Minimum rotation speed can be modified by controller (°/s) ~-~ 
Current rotation speed when controlled by controller (°/s) ~-~ 
Activate joystick when the DI is on, ignore it if it equals to -1 ~-~ 
di is off, can't use joystick ~-~ 
Using the speed of motors to calculate odometer ~-~ 
standalone ~-~ 
server ~-~ 
ip:port ~-~ 
RFID Sensor ~-~ 
uart port for rs485 ~-~ 
RFIDSensor init failed! ~-~ 
RFIDSensor doRun timeout! ~-~ 
RFIDSensor update timeout! ~-~ 
Absence of certain fields in rec file. ~-~ 
Rec file not exist. ~-~ 
Cloud data is empty. ~-~ 
pixel_target is empty. ~-~ 
shelf_dir_angle or shelf_to_robot_angle is too big. ~-~ 
pallet_dir_angle or pallet_to_robot_angle is too big. ~-~ 
farthest detection distance ~-~ 
heigher will not be  detected ~-~ 
The Scope of Roi min pts num ~-~ 
auto pallet high precision mode ~-~ 
pallet realtime recognition ~-~ 
Laser Rec ~-~ 
measure result has shown there is no Goods on the pallet ~-~ 
measure result has shown goods's width exceeds threshold,which is {1} ~-~ 
measure result has shown goods's height exceeds threshold,which is {1} ~-~ 
measure result has shown goods's width and height exceeds threshold,which width is {1}  and height is {2} ~-~ 