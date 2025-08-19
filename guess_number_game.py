import random

def guess_number_game():
    """
    一个简单的猜数字游戏。
    玩家需要猜一个1到100之间的数字。
    """
    print("欢迎来到猜数字游戏！")
    print("我将想一个1到100之间的数字，你需要猜出来。")

    # 生成一个1到100之间的随机数
    secret_number = random.randint(1, 100)
    guesses_taken = 0
    score = 0

    while True:
        try:
            # 获取用户输入
            guess = int(input("请输入你的猜测: "))
            guesses_taken += 1

            # 判断用户猜测
            if guess < secret_number:
                print("太低了！再试一次。")
            elif guess > secret_number:
                print("太高了！再试一次。")
            else:
                print(f"恭喜你！你猜对了，数字是 {secret_number}！")
                print(f"你一共猜了 {guesses_taken} 次。")

                # 简单的计分机制：猜测次数越少，分数越高
                # 假设最高分是100，根据猜测次数递减
                score = max(0, 100 - (guesses_taken - 1) * 5) # 每次多猜一次扣5分，最低0分
                print(f"你的得分是: {score}")
                break # 猜对了，退出循环

        except ValueError:
            print("无效输入！请输入一个整数。")

    return score # 返回本次游戏的得分

if __name__ == "__main__":
    # 如果直接运行此文件，则启动游戏
    guess_number_game()