import math
import keras
from keras import models
from keras import layers
import numpy as np



def basic_block(y,K,args,ishape=0,residual=0):

    if (residual):
        x=y

    str=np.ones(args.autonconv)
    if (residual):
        str[args.autonconv-1]=2
    str=np.int32(str)

    for i in range(args.autonconv):
        if (args.autocdwise==False):
            y=layers.Conv2D(K, kernel_size=(3, 3), strides=(str[i],str[i]), padding='same')(y)
        else:
            y=layers.SeparableConv2D(K,kernel_size=(3, 3), strides=(str[i],str[i]), padding='same')(y)

        y=layers.BatchNormalization()(y)
        if (args.da_gauss!=0.0):
            y=layers.GaussianNoise(0.3)(y)
        if (residual==0)|(i<args.autonconv-1):
            y=layers.ReLU()(y)


    if (residual):
         if (args.autocdwise==False):
             x=layers.Conv2D(K, kernel_size=(1, 1), strides=(2,2),padding='same')(x)
         else:
             x=layers.SeparableConv2D(K, kernel_size=(1, 1), strides=(2,2),padding='same')(x)
         y=layers.add([x, y])
         y=layers.ReLU()(y)

    else:
        y=layers.MaxPooling2D(pool_size=(2, 2))(y)
    return y


def auto_model(args,num_classes):

    h=args.height
    w=args.width
    if (args.chan=="rgb"):
        shape=(h,w,3)
    else:
        shape=(h,w,1)

    s=min(h,w)

    DEPTH=int(math.log2(s))
    KINI=args.autokini
    KEND=args.autokend

    print("Depth=",DEPTH)

    ##model = Sequential()
    numf=int(KINI/2)
    for i in range(DEPTH):
        numf=numf*2
        if (numf>KEND):
            numf=KEND

        res=0
        if ((args.auto_res==True)&(DEPTH>1)):
            res=1

        if (i==0):
            image_tensor = layers.Input(shape=shape)
            x=basic_block(image_tensor,numf,args)
        else:
            x=basic_block(x,numf,args,residual=res)


    x=layers.Flatten()(x)
    for i in range(args.autodlayers):
        x=layers.Dense(args.autodsize)(x)
        x=layers.BatchNormalization()(x)
        if (args.da_gauss!=0.0):
            x=layers.GaussianNoise(0.3)(x)
        x=layers.ReLU()(x)

    x=layers.Dense(num_classes, activation='softmax')(x)
    model = models.Model(inputs=[image_tensor], outputs=[x])

    return model
