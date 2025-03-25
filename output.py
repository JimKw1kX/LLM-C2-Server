import sys
import time
import argparse

from train import *
# from badgertab import 

# Initialize the model

def output():
    parser = argparse.ArgumentParser(description='Usage llm [number of loops] [number of tokens]\n\n e.g llm 2 100')
    parser.add_argument('arg1', type=int, help='number of loops')
    parser.add_argument('arg2', type=int, help='number of tokens')
    args = parser.parse_args()
    interate = args.arg1
    tokens = args.arg2

    model = bigram().to(device)

    # Load the model's state dictionary
    state = torch.load('/home/kali/Documents/bible_wigets_inter100000.pth', map_location=device)
    model_state_dict = state['model_state_dict']
    model.load_state_dict(model_state_dict)
    loss_value = state['loss']  # Extract the loss value
    epoch = state.get('epoch', 'N/A')
    print(f"Last loss value from training: {loss_value:.4f}")
    print(f"Model was saved after iteration: {epoch}")

    # Set model to evaluation mode
    model.eval()

    # Generate text
    for _ in range(interate):
        context = torch.zeros((1, 1), dtype=torch.long, device=device)  # Start token
        generated_indices = model.generate(context, max_new_tokens=tokens)[0].tolist()
        words = decode(generated_indices)
        for char in words:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.01)
        sys.stdout.write("\n" + '-' * 90 + "\n")
        sys.stdout.flush()





if __name__ == '__main__':

    output()