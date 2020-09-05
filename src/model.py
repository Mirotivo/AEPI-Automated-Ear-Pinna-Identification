class Net(nn.Module):
    def __init__(self):
        super(Net,self).__init__()
        self.NUM_CLASSES = 164
        self.levels = [4,2,1]
        model = models.vgg19_bn(pretrained=True)
        
        self.feature_extractor = nn.Sequential(*(list(model.children())[:-1]))
        #self.fc1 = nn.Linear(2048,1024)
        self.fc2 = nn.Linear(2048,512)
        self.fc3 = nn.Linear(512,self.NUM_CLASSES)
        self.dropout = nn.Dropout(p=0.3)

    def forward(self,x):
        x = self.feature_extractor(x)
       
        #x = self.spatial_pyramid_pool(x,[int(x.size(2)),int(x.size(3))],"max")
        #x = self.dropout(x)
        x = x.view(-1,2048)
        #x = self.fc1(x)
        #x = self.dropout(x)
        x = self.fc2(x)
        x = self.dropout(x)
        x = self.fc3(x)
        return x
    
    def spatial_pyramid_pool(self,previous_conv, previous_conv_size, mode ):
        
        num_sample = previous_conv.size(0)
        previous_conv_size = [int(previous_conv.size(2)), int(previous_conv.size(3))]
        for i in range(len(self.levels)):
            h_kernel = int(math.ceil(previous_conv_size[0] / self.levels[i]))
            w_kernel = int(math.ceil(previous_conv_size[1] / self.levels[i]))
            w_pad1 = int(math.floor((w_kernel * self.levels[i] - previous_conv_size[1]) / 2))
            w_pad2 = int(math.ceil((w_kernel * self.levels[i] - previous_conv_size[1]) / 2))
            h_pad1 = int(math.floor((h_kernel * self.levels[i] - previous_conv_size[0]) / 2))
            h_pad2 = int(math.ceil((h_kernel * self.levels[i] - previous_conv_size[0]) / 2))
            assert w_pad1 + w_pad2 == (w_kernel * self.levels[i] - previous_conv_size[1]) and \
                   h_pad1 + h_pad2 == (h_kernel * self.levels[i] - previous_conv_size[0])

            padded_input = F.pad(input=previous_conv, pad=[w_pad1, w_pad2, h_pad1, h_pad2],
                                 mode='constant', value=0)
            if mode == "max":
                pool = nn.MaxPool2d((h_kernel, w_kernel), stride=(h_kernel, w_kernel), padding=(0, 0))
            elif mode == "avg":
                pool = nn.AvgPool2d((h_kernel, w_kernel), stride=(h_kernel, w_kernel), padding=(0, 0))
            else:
                raise RuntimeError("Unknown pooling type: %s, please use \"max\" or \"avg\".")
            x = pool(padded_input)
            if i == 0:
                spp = x.view(num_sample, -1)
            else:
                spp = torch.cat((spp, x.view(num_sample, -1)), 1)

        return spp