import torch
import torch.nn as nn
from torch.nn import functional as F

# hyper parms--------
#----------------------------
batch_size = 64
block_size = 256
max_iters = 5000
eval_interval = 300
lr = 3e-4
device = 'cuda' if torch.cuda.is_available() else 'cpu'
eval_iters = 200
n_embd = 384
n_head = 6
n_layer = 6
dropout = 0.2

#----------------------------
# batch_size = 16
# block_size = 32
# max_iters = 5000
# eval_interval = 100
# learning_rate = 1e-3
# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# eval_iters = 200
# n_embd = 64
# lr = 3e-4
# n_head = 4
# n_layer = 4
# dropout = 0.2
# ------

torch.manual_seed(1337)

with open('/home/kali/Documents/bible.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# unique chars
chars = sorted(list(set(text)))
vocab_size = len(chars)

# mapping
stoi = {ch:i for i, ch in enumerate(chars)}
itos = {i:ch for i, ch in enumerate(chars)}
encode = lambda s: [stoi[c] for c in s]
decode = lambda l: ''.join([itos[i] for i in l])

# train and val splits
data = torch.tensor(encode(text), dtype=torch.long)
n = int(0.9*len(data))
train = data[:n]
val = data[n:]

# data loading
def get_batch(split):   
    # generate samll batches
    data = train if split == 'train' else val
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i: i + block_size] for i in ix])
    y = torch.stack([data [i+1:i+block_size+1] for i in ix])
    x ,y = x.to(device), y.to(device)
    return x,y

@torch.no_grad() # not to call loss.backward()
def estimate_loss():
    out = {}
    model.eval()
    for split in ['train', 'val']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split)
            logits, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out


class Head(nn.Module):
    # one head of self-attension
    def __init__(self, head_size):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(block_size,block_size)))

        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        B,T,C = x.shape
        k = self.key(x)
        q = self.query(x)
        # compute attenion scores ()
        wei = q @ k.transpose(-2,-1) * C**-0.5 # (B,T,C) @ (B,C,T) -> (B,T,T)
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf')) # (B,T,T)
        wei = F.softmax(wei, dim=-1) # b,t,t
        wei = self.dropout(wei) 
        
        # weighted aggregation of the values
        v = self.value(x) # (B,T,C)
        out = wei @ v # (b,t,t) @ (b,t,c) -> (b,t,c)
        return out


class MutiHeadAttention(nn.Module):
    """ mutiple heads of self-attension in parallel"""

    def __init__(self, num_heads, head_size):
        super().__init__()
        self.heads = nn.ModuleList([Head(head_size) for _ in range(num_heads)])
        self.proj = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x ):
        out = torch.cat([h(x) for h in self.heads], dim=-1) # dim is 2 (or -1) NOT 1!!! else will get error of :RuntimeError: mat1 and mat2 shapes cannot be multiplied (98304x64 and 384x384)
        out = self.dropout(self.proj(out))
        return out
    
class FeedFoward(nn.Module):
    """ a simple linearr layer followed by a non-lineraity"""

    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.ReLU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self ,x ):
        return self.net(x)


class Block(nn.Module):
    """transformer block: communication followed by computaion"""

    def __init__(self, n_embd, n_head):
        super().__init__()
        head_size = n_embd // n_head
        self.sa = MutiHeadAttention(n_head, head_size)
        self.ffwd = FeedFoward(n_embd)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)
        
    def forward(self ,x ):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x
    
class bigram(nn.Module):
    
    def __init__(self):
        super().__init__()
        #  each token directly reads off the logits for the next token from a loopup table
        self.token_embdding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embdding_table = nn.Embedding(block_size, n_embd)
        # self.sa_head = MutiHeadAttention(4, n_embd//4) # i.e 4 heads of 8 dimensional self-attension
        # self.blocks = nn.Sequential(
        #     Block(n_embd, n_head=4),
        #     Block(n_embd, n_head=4),
        #     Block(n_embd, n_head=4),
        #     nn.LayerNorm(n_embd),
        # )
        self.blocks = nn.Sequential(*[Block(n_embd, n_head=n_head) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)
       
        # self.ffwd = FeedFoward(n_embd)
         

    def forward(self, idx, targets=None):
        B,T = idx.shape
        # idx and targets are both (B, T) tensor of integers
        token_emb = self.token_embdding_table(idx) # (B,T,C)
        pos_emb = self.position_embdding_table(torch.arange(T, device=device)) # (T,C)
        x = token_emb + pos_emb # (B,T,C)
        x = self.blocks(x) # apply one head of self-attenion (B,T,C)
        x = self.ln_f(x) # b,t,c
        logits = self.lm_head(x) # (B, T, vocab_size)

        if targets is None:
            loss = None
        else:
            B,T,C = logits.shape
            logits = logits.view(B*T, C) # 2 dim
            targets = targets.view(-1) # 1 dim
            loss = F.cross_entropy(logits, targets)

        return logits, loss # score for the next sequences 
        # the loss should be 
        # -In(1/65)
    
    def generate(self, idx, max_new_tokens):

        for _ in range(max_new_tokens):
            # crop idx to the last block_size tokens
            idx_coud = idx[:, -block_size:]
            # get the predictions
            logits, loss = self(idx_coud)
            # focus only on the last time step
            logits = logits[:, -1, :] # (B,C)
            # get probalilituies
            probs = F.softmax(logits, dim=-1)
            #sample from distribution
            idx_next = torch.multinomial(probs, num_samples=1) # (B, 1)
            # append sampled index to the running sequence
            idx = torch.cat((idx, idx_next), dim=1) # (B, T+1)
            
        return idx



# train the network
model = bigram()
m = model.to(device)
state_name = 'bible_wigets.pth'
import time

if __name__ == '__main__': # only executes when run this script to prevent the output script to execute the trainning loop
    print(f'using {device}')
    print(sum(p.numel() for p in m.parameters())/1e6, 'M parameters')

    ops  = torch.optim.AdamW(m.parameters(), lr=lr)
    t0 = time.time()
    for iter in range(max_iters):
        # sample batches
        if iter % eval_interval == 0:
            losses = estimate_loss()
            # print(f'step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}')

        xb ,yb = get_batch('train')

        # evl
        logits, loss = model(xb, yb)
        ops.zero_grad(set_to_none=True)
        loss.backward()
        ops.step()

    t1 = time.time()
    time_train = (t1 - t0) * 1000
    
    print(f'It took {time_train} to train')
    
    state = {
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': ops.state_dict(),  # Optional: save optimizer state
    'loss': loss.item(),  # Save the last loss value
    'epoch': iter  # Optional: save the current epoch or iteration
    }

    torch.save(state, f'{state_name}')
    print(f"Model state saved to {state_name}")
