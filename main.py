from env_3d import Env3D
import matplotlib.pyplot as plt
import os
import imageio  # pip install imageio

def main():
    env = Env3D(auto=True, FPS=int(1e6), points=int(1e3))

    count = 1
    idx = 0

    os.makedirs('agent_views', exist_ok=True)

    running = True

    view_ls = []

    while running:
        running = env.step()
        view = env.capture_view()

        # if count % 100 == 0:
            # plt.figure(figsize=(10, 8))
            # plt.imshow(view)
            # plt.axis('off')
            # plt.title('Current Agent View')
            # plt.show()

        if count % 100 == 0:
            view_ls.append(view)
            
        count += 1

    for view in view_ls:
        filename = f'agent_views/view_{idx:06d}.png'
        imageio.imwrite(filename, view)
        idx += 1

    env.print_trajectory()


if __name__ == "__main__":
    main()