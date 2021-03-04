import numpy as np
import matplotlib.pyplot as plt
from PIL import ImageStat, Image

import skimage
from skimage import io
from skimage.transform import resize
from skimage import exposure, img_as_ubyte

from imgcat import imgcat

# ---

#from scripts.type_conversion import int16_to_uint8, uint8_to_norm, norm_to_uint8
import numpy as np

def int16_to_uint8(img):
    """range: -32,768 ～ 32,767"""
    img  = (img + 65536//2) # int16 -> uint16
    img = (img / 255).astype(np.uint8) # uint16 -> uint8
    return img

def uint8_to_norm(img):
    """range: 0-255 -> 0.0f-1.0f"""
    return img.astype(np.float32)/255

def norm_to_uint8(img):
    """range: 0.0f-1.0f -> 0-255"""
    return (img*255).astype(np.int)

#import matplotlib 
#matplotlib.use('agg')

class ImageChain:
	"""
	ImgObj:
		(transform)
			crop: crop a image
			clip: clip(truncate) value
			norm: TBD
			norm_zscore: TBD
			scale: scale(shrink) a image
			align: scale a image (to decided width)
		(print)
			status: print status
			show: show image by matplot
			show3d: image value as height by matplot
			iterm_show: show a image through iterm2
			hist: show image histgram
		(operation)
			add
			mul
		(handle)
			get: return self.img
			end: delete self.img
	"""
	def __init__(self):
		self.img = None
		self.fname = "unknown.unknown"

	def load(self, path: str):
		self.img = io.imread(path)
		self.fname = path.split("/")[-1]
		return self

	def show_fname(self, endl=None):
		print(f"filename: {self.fname}")
		if(endl!=None): print(endl)
		return self

	def set_img(self, img):
		self.img = img
		return self

	def crop(self, crop_size: "(height, width)", pos=["center", "left-top", "right-top", "left-bottom", "right-bottom"][0]) -> None:
		H, W = self.__get_height(), self.__get_width()
		cH, cW = crop_size

		if(pos=="center"):
			pH, pW = self.__get_center()
		elif(pos=="left-top" or pos=="right-top" or pos=="left-bottom" or "right-bottom"):
			pass
		else:
			raise ValueError("invalid pos")

		self.img = self.img[pH-(cH//2):pH+(cH//2),  pW-(cW//2):pW+(cW//2)]
		return self

	def clip(self, value=(0.0, 1.0)) -> "self":
		a_min, a_max = value
		np.clip(self.img, a_min=0.0, a_max=1.0)
		return self

	def norm(self, method) -> "self":
		if(method=="int16_to_uint8"):
			self.img = int16_to_uint8(self.img)
		elif(method=="uint8_to_norm"):
			self.img = uint8_to_norm(self.img)
		elif(method=="norm_to_uint8"):
			self.img = norm_to_uint8(self.img)
		else:
			raise ValueError("invalid method")
		return self

	def scale(self, ratio: int) -> "self":
		self.img = resize(image=self.img, output_shape=[self.__get_height()//ratio, self.__get_width()//ratio])
		return self

	def align(self, width: int) -> "self":
		return self.scale(ratio=W/width)

	def status(self, tabs=1, endl=None) -> "self":
		_tabs = "\t"*tabs
		img = self.img
		_dtype_full = f'{type(img)}'
		_dtype_1px = f'{type(img.flatten()[0])}'

		print("<<Image Statistics>>")
		# :と<の間にスペース無いとバグる。<と数字の間にスペースが有ると比較演算になってバグる
		print(f"{'max': <15} {_tabs}| {np.max(img):.4f}")
		print(f"{'min': <15} {_tabs}| {np.min(img):.4f}")
		print(f"{'mean': <15} {_tabs}| {np.mean(img):.4f}")
		print(f"{'std': <15} {_tabs}| {np.std(img):.4f}")
		print(f"{'median': <15} {_tabs}| {np.std(img):.4f}")	
		print("---\n")
		print(f"<<pixel information>>")
		print(f"{'shape': <15} {_tabs}| {f'{img.shape}': >25}")
		print(f"{'num_pixels': <15} {_tabs}| {str(self.__get_height()*self.__get_width()): >25}")
		print(f"{'dtype': <15} {_tabs}| {_dtype_full: >25}")
		print(f"{'dtype (1px)': <15} {_tabs}| {_dtype_1px: >25}")

		if(endl!=None): print(endl)
		return self

	def show(self) -> "self":
		plt.figure()
		if(len(self.img.shape)==3):
			plt.imshow(self.img)
		else:
			plt.imshow(self.img, cmap = "gray", vmin=0.0, vmax=1.0)
		plt.show()
		plt.close()
		return self

	def show3d(self) -> "self":
		H, W = np.meshgrid(
			  np.linspace(start=0, stop=self.__get_height(), num=self.__get_height())
			, np.linspace(start=0, stop=self.__get_width(), num=self.__get_width())
			)

		ax = plt.axes(projection='3d')
		ax.plot_surface(H, W, self.img, rstride=1, cstride=1,
						cmap='viridis', edgecolor='none')
		ax.set_title('3D Plotting')
		return self

	def iterm_show(self) -> "self":
		im = skimage.data.chelsea()   # [300, 451, 3] ndarray, dtype=uint8
		imgcat(self.img, height=7)
		return self

	def hist(self, dtype="int16") -> "self":
		plt.figure()
		if(dtype=="int16"):
			plt.hist(img_as_ubyte(self.img.flatten()), bins=np.arange(65536+1))
		else:
			plt.hist(img_as_ubyte(exposure.rescale_intensity(self.img)).flatten(), bins=np.arange(256+1))
		plt.show()
		return self

	def add(self, val: float) -> "self":
		self.img += val
		return self

	def mul(self, val: float) -> "self":
		self.img *= val
		return self

	def get(self) -> "image":
		return self.img

	def end(self) -> None:
		del self.img
		return None

	def __get_width(self) -> int:
		return self.img.shape[1]

	def __get_height(self) -> int:
		return self.img.shape[0]

	def __get_center(self) -> "tuple(height, width)":
		return (self.__get_height(), self.__get_width())