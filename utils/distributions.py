import math

import torch
import torch.nn as nn
import torch.nn.functional as F

# from utils.weights_init import AddBias, init, init_normc_

FixedCategorical = torch.distributions.Categorical

old_sample = FixedCategorical.sample
FixedCategorical.sample = lambda self: old_sample(self).unsqueeze(-1)

log_prob_cat = FixedCategorical.log_prob
FixedCategorical.log_probs = lambda self, actions: log_prob_cat(self, actions.squeeze(-1)).unsqueeze(-1)

FixedCategorical.mode = lambda self: self.probs.argmax(dim=1, keepdim=True)


class Categorical(nn.Module):
    def __init__(self):
        super(Categorical, self).__init__()

        # init_ = lambda m: init(m,
        #       nn.init.orthogonal_,
        #       lambda x: nn.init.constant_(x, 0),
        #       gain=0.01)

        # self.linear = init_(nn.Linear(num_inputs, num_outputs))
        # self.linear = nn.Linear(num_inputs, num_outputs)

    def act(self, input, mask=None):
        x = F.softmax(input, dim=1)
        if mask is not None:
            x = x * mask
        return FixedCategorical(probs=x)

    def forward(self, *args):
        raise NotImplementedError
