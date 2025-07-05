import pygame
pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("键盘输入测试")
clock = pygame.time.Clock()

print("测试开始！按WASD键测试输入，ESC键退出")

while True:
    # 检测按键状态（持续按下）
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: print("W 键被按住")
    if keys[pygame.K_a]: print("A 键被按住")
    if keys[pygame.K_s]: print("S 键被按住")
    if keys[pygame.K_d]: print("D 键被按住")
    if keys[pygame.K_ESCAPE]: break  # ESC退出
    
    # 检测按键事件（按下/释放）
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            print(f"[事件] 按键按下: {pygame.key.name(event.key)}")
        if event.type == pygame.KEYUP:
            print(f"[事件] 按键释放: {pygame.key.name(event.key)}")
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("测试结束")