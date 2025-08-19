import os
import sys
import random
import time
import msvcrt # 用于Windows下的非阻塞输入

# 游戏常量
GRID_WIDTH = 20
GRID_HEIGHT = 10
SNAKE_SPEED = 0.2 # 初始速度，秒/步

class Snake:
    def __init__(self):
        # 蛇的初始位置在网格中心
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)] 
        # 初始方向：向上 (x, y) -> (0, -1)
        self.direction = (0, -1) 
        self.grow = False

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        self.body.insert(0, new_head)

        if not self.grow:
            self.body.pop() # 如果没有增长，移除最后一个节点
        else:
            self.grow = False # 重置增长标志

    def change_direction(self, new_direction):
        # 防止蛇立即掉头
        # new_direction[0] * -1 是新方向的x分量的反向，new_direction[1] * -1 是新方向的y分量的反向
        # 如果新方向的反向等于当前方向，则说明是掉头，不允许改变
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def grow_snake(self):
        self.grow = True

    def check_collision(self):
        head = self.body[0]
        # 撞墙检查
        if not (0 <= head[0] < GRID_WIDTH and 0 <= head[1] < GRID_HEIGHT):
            return True
        # 撞到自身检查 (排除蛇头本身)
        if head in self.body[1:]:
            return True
        return False

class Food:
    def __init__(self, snake_body):
        self.position = (0, 0)
        self.snake_body = snake_body # 传递蛇的身体列表，用于生成食物时避开蛇
        self.respawn()

    def respawn(self):
        # 确保食物不会生成在蛇的身体上
        while True:
            new_pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if new_pos not in self.snake_body:
                self.position = new_pos
                break

def draw_grid(snake, food, score):
    # 清屏 (兼容Windows和Linux)
    os.system('cls' if os.name == 'nt' else 'clear')

    # 创建一个空白的网格
    grid = [[' ' for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    # 绘制食物
    food_x, food_y = food.position
    # 确保食物位置在网格内（虽然respawn应该保证了，但为了安全）
    if 0 <= food_x < GRID_WIDTH and 0 <= food_y < GRID_HEIGHT:
        grid[food_y][food_x] = '*'

    # 绘制蛇
    for i, (x, y) in enumerate(snake.body):
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            grid[y][x] = '#' if i == 0 else 'o' # 蛇头是#, 身体是o

    # 绘制边框
    print('+' + '-' * GRID_WIDTH + '+')
    for row in grid:
        print('|' + ''.join(row) + '|')
    print('+' + '-' * GRID_WIDTH + '+')
    print(f"Score: {score}")
    print("Controls: W=Up, S=Down, A=Left, D=Right, Q=Quit")

def get_key_press():
    # 检查是否有键盘输入，并返回按键（小写）
    if msvcrt.kbhit(): 
        key = msvcrt.getch()
        return key.decode('utf-8').lower() 
    return None

def main():
    snake = Snake()
    # 在初始化Food时，将snake.body传递给它
    food = Food(snake.body) 
    score = 0

    while True:
        draw_grid(snake, food, score)
        
        key = get_key_press()
        
        # 处理用户输入
        if key == 'q':
            print("Quitting game.")
            break
        elif key == 'w':
            snake.change_direction((0, -1)) # 向上
        elif key == 's':
            snake.change_direction((0, 1))  # 向下
        elif key == 'a':
            snake.change_direction((-1, 0)) # 向左
        elif key == 'd':
            snake.change_direction((1, 0))  # 向右

        # 移动蛇
        snake.move()

        # 检查碰撞 (墙壁或自身)
        if snake.check_collision():
            print("Game Over!")
            break

        # 检查食物碰撞
        if snake.body[0] == food.position:
            snake.grow_snake() # 蛇增长
            food.respawn()     # 重新生成食物
            score += 1         # 分数增加
            # 游戏速度可以根据得分逐渐加快 (可选)
            # global SNAKE_SPEED
            # if score % 5 == 0: # 每得5分加速一次
            #     SNAKE_SPEED *= 0.95 

        # 控制游戏速度
        time.sleep(SNAKE_SPEED)

if __name__ == "__main__":
    main()