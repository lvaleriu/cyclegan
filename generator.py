from keras.layers import Conv2D, Conv2DTranspose, UpSampling2D
from keras.layers import BatchNormalization, Activation, Input, ZeroPadding2D
from keras.layers.merge import Add, Concatenate
from keras.models import Model

from utils import get_filter_dim
from layers import ReflectPadding2D, InstanceNormalization2D


'''
*****************************************************************************
********************************  defineG   *********************************
*****************************************************************************
'''
def defineG(which_model_netG, input_shape, output_shape, ngf, **kwargs):
    output_nc = output_shape[get_filter_dim()-1]
    if which_model_netG == 'resnet_6blocks':
        return resnet_6blocks(input_shape, output_nc, ngf, **kwargs)
    else:
        raise NotImplemented

'''
*****************************************************************************
****************************  Generator: Resnet *****************************
*****************************************************************************
'''
padding = ZeroPadding2D # or use ReflectPadding2D

def normalize():
    #return BatchNormalization()#axis=get_filter_dim()
    return InstanceNormalization2D()

def scaleup(input, ngf, kss, strides, padding):
    x = UpSampling2D(strides)(input)
    x = Conv2D(ngf, kss, padding=padding)(x)
    return x

def res_block(input, filters, kernel_size=(3,3), strides=(1,1)):
    x = padding()(input)
    x = Conv2D(filters=filters,
                kernel_size=kernel_size,
                strides=strides,)(x)
    x = normalize()(x)
    x = Activation('relu')(x)

    x = padding()(x)
    x = Conv2D(filters=filters,
                kernel_size=kernel_size,
                strides=strides,)(x)
    x = normalize()(x)

    merged = Add()([input, x])
    return merged

def resnet_6blocks(input_shape, output_nc, ngf, **kwargs):
    ks = 3
    f = 7
    p = int((f-1)/2)

    input = Input(input_shape)
    x = padding((p,p))(input)
    x = Conv2D(ngf, (f,f),)(x)
    x = normalize()(x)
    x = Activation('relu')(x)

    x = Conv2D(ngf*2, (ks,ks), strides=(2,2), padding='same')(x)
    x = normalize()(x)
    x = Activation('relu')(x)

    x = Conv2D(ngf*4, (ks,ks), strides=(2,2), padding='same')(x)
    x = normalize()(x)
    x = Activation('relu')(x)

    x = res_block(x, ngf*4)
    x = res_block(x, ngf*4)
    x = res_block(x, ngf*4)
    x = res_block(x, ngf*4)
    x = res_block(x, ngf*4)
    x = res_block(x, ngf*4)

    x = scaleup(x, ngf*2, (ks, ks), strides=(2,2), padding='same')
    x = normalize()(x)
    x = Activation('relu')(x)

    x = scaleup(x, ngf, (ks, ks), strides=(2,2), padding='same')
    x = normalize()(x)
    x = Activation('relu')(x)

    x = padding((p,p))(x)
    x = Conv2D(output_nc, (f,f))(x)
    x = Activation('tanh')(x)

    model = Model(input, x, name=kwargs.get('name',None))
    print('Model resnet 6blocks:')
    model.summary()
    return model