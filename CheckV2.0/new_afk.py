# By 1234567890regis - luogu = RandomGuy1520 - github
# Some by 5793__qwq - luogu = 5793qwq - github
import cv2
import keyboard
import numpy as np
import sys
from PIL import Image
import pyautogui
import time
from time import sleep
from selenium.webdriver import Chrome, Edge, Firefox, Safari
import random
import math
import pytweening

def generate_random_curve_parameters(driver, pre_origin, post_destination):
    """Generates random parameters for the curve, the tween, number of knots, distortion, target points and boundaries"""
    web = False
    if isinstance(driver, (Chrome, Firefox, Edge, Safari)):
        web = True
        viewport_width, viewport_height = driver.get_window_size().values()
    else:
        viewport_width, viewport_height = driver.size()
    min_width, max_width = viewport_width * 0.15, viewport_width * 0.85
    min_height, max_height = viewport_height * 0.15, viewport_height * 0.85

    tween_options = [
        pytweening.easeOutExpo,
        pytweening.easeInOutQuint,
        pytweening.easeInOutSine,
        pytweening.easeInOutQuart,
        pytweening.easeInOutExpo,
        pytweening.easeInOutCubic,
        pytweening.easeInOutCirc,
        pytweening.linear,
        pytweening.easeOutSine,
        pytweening.easeOutQuart,
        pytweening.easeOutQuint,
        pytweening.easeOutCubic,
        pytweening.easeOutCirc,
    ]

    tween = random.choice(tween_options)
    offset_boundary_x = random.choice(
        random.choices(
            [range(20, 45), range(45, 75), range(75, 100)], [0.2, 0.65, 15]
        )[0]
    )
    offset_boundary_y = random.choice(
        random.choices(
            [range(20, 45), range(45, 75), range(75, 100)], [0.2, 0.65, 15]
        )[0]
    )
    knots_count = random.choices(
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [0.15, 0.36, 0.17, 0.12, 0.08, 0.04, 0.03, 0.02, 0.015, 0.005],
    )[0]

    distortion_mean = random.choice(range(80, 110)) / 100
    distortion_st_dev = random.choice(range(85, 110)) / 100
    distortion_frequency = random.choice(range(25, 70)) / 100

    if web:
        target_points = random.choice(
            random.choices(
                [range(35, 45), range(45, 60), range(60, 80)], [0.53, 0.32, 0.15]
            )[0]
        )
    else:
        target_points = max(int(math.sqrt((pre_origin[0] - post_destination[0]) ** 2 + (pre_origin[1] - post_destination[1]) ** 2)), 2)

    if (
            min_width > pre_origin[0]
            or max_width < pre_origin[0]
            or min_height > pre_origin[1]
            or max_height < pre_origin[1]
    ):
        offset_boundary_x = 0
        offset_boundary_y = 0
        knots_count = 1
    if (
            min_width > post_destination[0]
            or max_width < post_destination[0]
            or min_height > post_destination[1]
            or max_height < post_destination[1]
    ):
        offset_boundary_x = 0
        offset_boundary_y = 0
        knots_count = 1

    return (
        offset_boundary_x,
        offset_boundary_y,
        knots_count,
        distortion_mean,
        distortion_st_dev,
        distortion_frequency,
        tween,
        target_points,
    )


class HumanizeMouseTrajectory:
    def __init__(self, from_point, to_point, **kwargs):
        self.from_point = from_point
        self.to_point = to_point
        self.points = self.generate_curve(**kwargs)

    def generate_curve(self, **kwargs):
        """Generates the curve based on arguments below, default values below are automatically modified to cause randomness"""
        offset_boundary_x = kwargs.get("offset_boundary_x", 80)
        offset_boundary_y = kwargs.get("offset_boundary_y", 80)
        left_boundary = (
            kwargs.get("left_boundary", min(self.from_point[0], self.to_point[0]))
            - offset_boundary_x
        )
        right_boundary = (
            kwargs.get("right_boundary", max(self.from_point[0], self.to_point[0]))
            + offset_boundary_x
        )
        down_boundary = (
            kwargs.get("down_boundary", min(self.from_point[1], self.to_point[1]))
            - offset_boundary_y
        )
        up_boundary = (
            kwargs.get("up_boundary", max(self.from_point[1], self.to_point[1]))
            + offset_boundary_y
        )
        knots_count = kwargs.get("knots_count", 2)
        distortion_mean = kwargs.get("distortion_mean", 1)
        distortion_st_dev = kwargs.get("distortion_st_dev", 1)
        distortion_frequency = kwargs.get("distortion_frequency", 0.5)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)
        target_points = kwargs.get("target_points", 100)

        internalKnots = self.generate_internal_knots(
            left_boundary, right_boundary, down_boundary, up_boundary, knots_count
        )
        points = self.generate_points(internalKnots)
        points = self.distort_points(
            points, distortion_mean, distortion_st_dev, distortion_frequency
        )
        points = self.tween_points(points, tween, target_points)
        return points

    def generate_internal_knots(
        self, l_boundary, r_boundary, d_boundary, u_boundary, knots_count
    ):
        """Generates the internal knots of the curve randomly"""
        if not (
            self.check_if_numeric(l_boundary)
            and self.check_if_numeric(r_boundary)
            and self.check_if_numeric(d_boundary)
            and self.check_if_numeric(u_boundary)
        ):
            raise ValueError("Boundaries must be numeric values")
        if not isinstance(knots_count, int) or knots_count < 0:
            knots_count = 0
        if l_boundary > r_boundary:
            raise ValueError(
                "left_boundary must be less than or equal to right_boundary"
            )
        if d_boundary > u_boundary:
            raise ValueError(
                "down_boundary must be less than or equal to upper_boundary"
            )
        try:
            knotsX = np.random.choice(range(l_boundary, r_boundary) or l_boundary, size=knots_count)
            knotsY = np.random.choice(range(d_boundary, u_boundary) or d_boundary, size=knots_count)
        except TypeError:
            knotsX = np.random.choice(
                range(int(l_boundary), int(r_boundary)), size=knots_count
            )
            knotsY = np.random.choice(
                range(int(d_boundary), int(u_boundary)), size=knots_count
            )
        knots = list(zip(knotsX, knotsY))
        return knots

    def generate_points(self, knots):
        """Generates the points from BezierCalculator"""
        if not self.check_if_list_of_points (knots):
            raise ValueError("knots must be valid list of points")

        midPtsCnt = max(
            abs(self.from_point[0] - self.to_point[0]),
            abs(self.from_point[1] - self.to_point[1]),
            2,
        )
        knots = [self.from_point] + knots + [self.to_point]
        return BezierCalculator.calculate_points_in_curve(int(midPtsCnt), knots)

    def distort_points(
        self, points, distortion_mean, distortion_st_dev, distortion_frequency
    ):
        """Distorts points by parameters of mean, standard deviation and frequency"""
        if not (
            self.check_if_numeric(distortion_mean)
            and self.check_if_numeric(distortion_st_dev)
            and self.check_if_numeric(distortion_frequency)
        ):
            raise ValueError("Distortions must be numeric")
        if not self.check_if_list_of_points(points):
            raise ValueError("points must be valid list of points")
        if not (0 <= distortion_frequency <= 1):
            raise ValueError("distortion_frequency must be in range [0,1]")

        distorted = []
        for i in range(1, len(points) - 1):
            x, y = points[i]
            delta = (
                np.random.normal(distortion_mean, distortion_st_dev)
                if random.random() < distortion_frequency
                else 0
            )
            distorted += ((x, y + delta),)
        distorted = [points[0]] + distorted + [points[-1]]
        return distorted

    def tween_points(self, points, tween, target_points):
        """Modifies points by tween"""
        if not self.check_if_list_of_points(points):
            raise ValueError("List of points not valid")
        if not isinstance(target_points, int) or target_points < 2:
            raise ValueError("target_points must be an integer greater or equal to 2")

        res = []
        for i in range(target_points):
            index = int(tween(float(i) / (target_points - 1)) * (len(points) - 1))
            res += (points[index],)
        return res

    @staticmethod
    def check_if_numeric(val):
        """Checks if value is proper numeric value"""
        return isinstance(val, (float, int, np.int32, np.int64, np.float32, np.float64))

    def check_if_list_of_points(self, list_of_points):
        """Checks if list of points is valid"""
        if not isinstance(list_of_points, list):
            return False
        try:
            point = lambda p: (
                (len(p) == 2)
                and self.check_if_numeric(p[0])
                and self.check_if_numeric(p[1])
            )
            return all(map(point, list_of_points))
        except (KeyError, TypeError):
            return False


class BezierCalculator:
    @staticmethod
    def binomial(n, k):
        """Returns the binomial coefficient "n choose k" """
        return math.factorial(n) / float(math.factorial(k) * math.factorial(n - k))

    @staticmethod
    def bernstein_polynomial_point(x, i, n):
        """Calculate the i-th component of a bernstein polynomial of degree n"""
        return BezierCalculator.binomial(n, i) * (x**i) * ((1 - x) ** (n - i))

    @staticmethod
    def bernstein_polynomial(points):
        """
        Given list of control points, returns a function, which given a point [0,1] returns
        a point in the Bezier curve described by these points
        """ 

        def bernstein(t):
            n = len(points) - 1
            x = y = 0
            for i, point in enumerate(points):
                bern = BezierCalculator.bernstein_polynomial_point(t, i, n)
                x += point[0] * bern
                y += point[1] * bern
            return x, y

        return bernstein

    @staticmethod
    def calculate_points_in_curve(n, points):
        """
        Given list of control points, returns n points in the Bezier curve,
        described by these points
        """
        curvePoints = []
        bernstein_polynomial = BezierCalculator.bernstein_polynomial(points)
        for i in range(n):
            t = i / (n - 1)
            curvePoints += (bernstein_polynomial(t),)
        return curvePoints


class SystemCursor:
    def __init__(self):
        pyautogui.MINIMUM_DURATION = 0
        pyautogui.MINIMUM_SLEEP = 0
        pyautogui.PAUSE = 0

    @staticmethod
    def move_to(point: list or tuple, duration: int or float = None, human_curve=None, steady=False):
        """Moves to certain coordinates of screen"""
        from_point = pyautogui.position()

        if not human_curve:
            (
                offset_boundary_x,
                offset_boundary_y,
                knots_count,
                distortion_mean,
                distortion_st_dev,
                distortion_frequency,
                tween,
                target_points,
            ) = generate_random_curve_parameters(
                pyautogui, from_point, point
            )
            if steady:
                offset_boundary_x, offset_boundary_y = 10, 10
                distortion_mean, distortion_st_dev, distortion_frequency = 1.2, 1.2, 1
            human_curve = HumanizeMouseTrajectory(
                from_point,
                point,
                offset_boundary_x=offset_boundary_x,
                offset_boundary_y=offset_boundary_y,
                knots_count=knots_count,
                distortion_mean=distortion_mean,
                distortion_st_dev=distortion_st_dev,
                distortion_frequency=distortion_frequency,
                tween=tween,
                target_points=target_points,
            )

        if duration is None:
            duration = random.uniform(0.5, 2.0)
        pyautogui.PAUSE = duration / len(human_curve.points)
        for pnt in human_curve.points:
            pyautogui.moveTo(pnt)
            # print(pnt)
        pyautogui.moveTo(point)

    @staticmethod
    def move_to_short(point: list or tuple, duration: int or float = None, human_curve=None, steady=False):
        """Moves to certain coordinates of screen"""
        from_point = pyautogui.position()
        from_point = (from_point[0] * 10, from_point[1] * 10)
        point[0] *= 10
        point[1] *= 10
        if not human_curve:
            (
                offset_boundary_x,
                offset_boundary_y,
                knots_count,
                distortion_mean,
                distortion_st_dev,
                distortion_frequency,
                tween,
                target_points,
            ) = generate_random_curve_parameters(
                pyautogui, from_point, point
            )
            if steady:
                offset_boundary_x, offset_boundary_y = 5, 5
                distortion_mean, distortion_st_dev, distortion_frequency = 1.1, 1.1, 1
            human_curve = HumanizeMouseTrajectory(
                from_point,
                point,
                offset_boundary_x=offset_boundary_x,
                offset_boundary_y=offset_boundary_y,
                knots_count=knots_count,
                distortion_mean=distortion_mean,
                distortion_st_dev=distortion_st_dev,
                distortion_frequency=distortion_frequency,
                tween=tween,
                target_points=target_points,
            )

        if duration is None:
            duration = random.uniform(0.5, 2.0)
        pyautogui.PAUSE = duration / len(human_curve.points)
        lst = [0, 0]
        for pnt in human_curve.points:
            if lst != [pnt[0] // 10, pnt[1] // 10]:
                pyautogui.moveTo(pnt[0] // 10, pnt[1] // 10)
                # print(pnt[0] // 10, pnt[1] // 10)
            lst = [pnt[0] // 10, pnt[1] // 10]
        pyautogui.moveTo(point[0] // 10, point[1] // 10)
        # print(point[0] // 10, point[1] // 10)

    def click_on(self, point: list or tuple, clicks: int = 1, click_duration: int or float = 0, steady=False):
        """Clicks a specified number of times, on the specified coordinates"""
        self.move_to(point, steady=steady)
        for _ in range(clicks):
            pyautogui.mouseDown()
            sleep(click_duration)
            pyautogui.mouseUp()
            sleep(random.uniform(0.170, 0.280))

    def drag_and_drop(self, from_point: list or tuple, to_point: list or tuple, duration: int or float or [float, float] or (float, float) = None, steady=False):
        """Drags from a certain point, and releases to another"""
        if isinstance(duration, (list, tuple)):
            first_duration, second_duration = duration
        elif isinstance(duration, (float, int)):
            first_duration = second_duration = duration / 2
        else:
            first_duration = second_duration = None

        self.move_to(from_point, duration=first_duration)
        pyautogui.mouseDown()
        self.move_to(to_point, duration=second_duration, steady=steady)
        pyautogui.mouseUp()

grey_colors = [[110, 135, 87], [107, 149, 157], [104, 142, 149], [93, 101, 113], [100, 112, 128], [111, 157, 165],
               [116, 144, 153], [108, 130, 139], [114, 143, 150], [96, 96, 96],
               [137, 149, 155], [141, 153, 159], [135, 146, 151], [161, 155, 143]]  # Desert

def is_grey(px):
    if (px == [79, 106, 111]).all() or (px == [84, 117, 123]).all() or (px == [82, 112, 117]).all():
        return False
    if 130 >= px[2] >= 100 >= px[0] >= 85 and 95 <= px[1] <= 115:
        return True
    for gc in grey_colors:
        if abs(px[0] - gc[0]) + abs(px[1] - gc[1]) + abs(px[2] - gc[2]) <= 30:
            return True
    return False

time.sleep(3)
sys.setrecursionlimit(5000)
rarities = [[109, 239, 126], [93, 230, 255], [227, 82, 77], [222, 31, 134], [31, 31, 222], [222, 219, 31],
            [117, 43, 255], [163, 255, 43]]
white = [255, 255, 254]
jump = 5
cursor = SystemCursor()
count = 0
dfs_cnt = 0

def dfs(x, y):
    global dfs_cnt
    dfs_cnt += 1
    if dfs_cnt > 4000:
        return
    global count
    if x < 0 or y < 0 or x >= img.shape[0] or y >= img.shape[1]:
        return
    if not (img[x][y] == white).all():
        return
    if vis[x][y]:
        return
    vis[x][y] = True
    count += 1
    next_coords = [(x - jump, y), (x + jump, y), (x, y - jump), (x, y + jump),
                   (x - 2 * jump, y), (x + 2 * jump, y), (x, y - 2 * jump), (x, y + 2 * jump),
                   (x - jump, y - jump), (x + jump, y - jump), (x - jump, y + jump), (x + jump, y + jump)]
    for coord in next_coords:
        dfs(coord[0], coord[1])

def move(number):
    pyautogui.keyDown('w')
    time.sleep(219)
    pyautogui.keyUp('w')
    pyautogui.keyDown('a')
    time.sleep(30)
    pyautogui.keyUp('a')
    pyautogui.keyDown('a')
    pyautogui.keyDown('s')
    time.sleep(90)
    pyautogui.keyUp('a')
    pyautogui.keyUp('s')
    pyautogui.keyDown('w')
    time.sleep(110)
    pyautogui.keyUp('w')
def move2(number):
    pyautogui.keyDown('l')
    pyautogui.keyDown('2')
    time.sleep(0.05)
    pyautogui.keyUp('l')
    pyautogui.keyUp('2')
    time.sleep(0.05)
    pyautogui.keyDown('a')
    time.sleep(30)
    pyautogui.keyUp('a')
    pyautogui.keyDown('a')
    pyautogui.keyDown('s')
    time.sleep(90)
    pyautogui.keyUp('a')
    pyautogui.keyUp('s')
    pyautogui.keyDown('w')
    time.sleep(110)
    pyautogui.keyUp('w')

while True:
    if keyboard.is_pressed('q'):
        break
    time.sleep(1)
    round_count = 0

while True:
    if keyboard.is_pressed('q'):
        break
    for people in range(2):
        imgObj = pyautogui.screenshot()
        imgArr = cv2.cvtColor(np.array(imgObj), cv2.COLOR_RGB2BGR)
        ready = Image.open("Images/Ready.PNG")
        continues = Image.open("Images/continue.PNG")
        try:
            box = pyautogui.locateOnScreen(ready, grayscale=False, confidence=0.8)
            if box is not None:
                x_center = box.left  + box.width  // 2  
                y_center = box.top  + box.height  // 2 
                pyautogui.click(x_center,  y_center)
                pyautogui.click()
                continue
        except:
            pass
        try:
            box = pyautogui.locateOnScreen(continues, grayscale=False, confidence=0.8)
            if box is not None:
                x_center = box.left  + box.width  // 2  
                y_center = box.top  + box.height  // 2 
                pyautogui.click(x_center,  y_center)
                for i in range(25):
                    try:
                        box = pyautogui.locateOnScreen(ready, grayscale=False, confidence=0.8)
                        if box is not None:
                            x_center = box.left  + box.width  // 2  
                            y_center = box.top  + box.height  // 2 
                            pyautogui.click(x_center,  y_center)
                        continue
                    except:
                        time.sleep(1)
                        pass
                move2(people)
                pyautogui.keyDown('l')
                pyautogui.keyDown('0')
                time.sleep(0.05)
                pyautogui.keyUp('l')
                pyautogui.keyUp('0')
                time.sleep(0.05)
                continue
        except:
            pass
        round_count = (round_count + 1) % 20
        cv2.imwrite("Log/log" + str(round_count) + ".png", imgArr)
        img = np.zeros((1400, 2200, 3))
        img[:imgArr.shape[0], :imgArr.shape[1]] = imgArr
        cv2.imwrite("new.PNG", img)
        vis = np.zeros((1400, 2200))
        for i in range(0, 300, jump):
            for j in range(0, 400, jump):
                img[i][j] = [0, 0, 0]
        for i in range(910, 1070, jump):
            for j in range(550, 1360, jump):
                img[i][j] = [0, 0, 0]
        for i in range(0, len(img), jump):
            for j in range(0, len(img[i]), jump):
                pixel = img[i][j]
                if is_grey(pixel):
                    img[i][j] = white
        cv2.imwrite("new.PNG", img)
        max_cluster = 0
        max_coord = (0, 0)
        for i in range(0, len(img), jump):
            for j in range(0, len(img[i]), jump):
                if (img[i][j] == white).all():
                    if not vis[i][j]:
                        count = 0
                        dfs_cnt = 0
                        dfs(i, j)
                        if count > max_cluster:
                            max_cluster = count
                            max_coord = (i, j)
        if max_cluster <= 15:
            continue
        vis = np.zeros((2000, 2000))
        dfs_cnt = 0
        dfs(max_coord[0], max_coord[1])
        sum_start, num_start = [0, 0], 0
        for i in range(0, len(img), 10):
            for j in range(0, len(img[i]), 10):
                pixel = img[i][j]
                flag = False
                for rarity in rarities:
                    if abs(rarity[0] - pixel[0]) + abs(rarity[1] - pixel[1]) + abs(rarity[2] - pixel[2]) <= 40:
                        for k in range(i - 25, i + 30, 5):
                            for l in range(j - 25, j + 30, 5):
                                if vis[k][l]:
                                    flag = True
                                    sum_start[0] += i
                                    sum_start[1] += j
                                    num_start += 1
                                    break
                            if flag:
                                break
                        if flag:
                            break
        if num_start == 0:
            continue
        start = ((sum_start[0] // num_start // jump) * jump, (sum_start[1] // num_start // jump) * jump)
        print("Detected:", start)
        cur = start
        stack = [cur]
        recur = 0
        while True:
            recur += 1
            if recur > 100:
                print("Maximum recursive exceeded!")
                stack = []
                break
            sum_cur, num_cur = [0, 0], 0
            for i in range(-25, 30, jump):
                for j in range(-25, 30, jump):
                    if i * i + j * j <= 625 and vis[cur[0] + i][cur[1] + j]:
                        sum_cur[0] += i
                        sum_cur[1] += j
                        num_cur += 1
            if num_cur == 0:
                break
            next_cur = ((cur[0] + sum_cur[0] // num_cur) // jump * jump, (cur[1] + sum_cur[1] // num_cur) // jump * jump)
            for i in range(-20, 25, jump):
                for j in range(-20, 25, jump):
                    if i * i + j * j <= 400:
                        img[cur[0] + i][cur[1] + j] = [0, 0, 0]
                        vis[cur[0] + i][cur[1] + j] = False
            cur = next_cur
            stack.append(next_cur)
        if not stack:
            continue
        cursor.move_to([stack[0][1], stack[0][0]])
        pyautogui.click()
        img[stack[0][0]][stack[0][1]] = [0, 255, 0]
        if len(stack) >= 2:
            for i in range(4):
                lst = stack[-1]
                lst_lst = stack[-2]
                stack.append((2 * lst[0] - lst_lst[0], 2 * lst[1] - lst_lst[1]))
        pyautogui.mouseDown()
        duration = 0.25
        for i in range(1, len(stack)):
            duration += random.uniform(-0.1, 0.1)
            if duration < 0.15:
                duration = 0.15
            if duration > 0.4:
                duration = 0.4
            cursor.move_to_short([stack[i][1], stack[i][0]], steady=True, duration=duration)
            img[stack[i][0]][stack[i][1]] = [0, 255, 0]
        pyautogui.mouseUp()
        cv2.imwrite("new.PNG", img)