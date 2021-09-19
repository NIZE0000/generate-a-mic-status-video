# generate-a-mic-status-video
generate a video from detection audio.
base on jumpcutter by kivancyuksel
all of this code used python.

## Installation
first you have to install all package requirements
```
pip install -r requirements.txt
```

## Command
*Required  
`--input`, `-i`: Path to the video or audio that you want to use for generate a video.  
`--output`, `-o`: Path to where you want to save the output video.  
`--default_img`, `-d_`: Path to the inactive image file.  
`--active_img`, `-a_`: Path to the active image file.  
  
*Addition  
`--width`, `-w_`:  If this parameter is given the width of video will change. *Default width reference frome default_img   
`--heigth`, `-h_`:  If this parameter is given the heigth of video will change. *Default heigth reference frome default_img  
`--silence-part-speed`, `-x`: If this parameter is given the silent part will speed up "x" times.  
`--fps` : Desired fps of the output video.  
`--bitrate` : Desired bitrate of the output video.   
`--codec`: Codec to use for image encoding.  
`--duration-threshold`, `-d`: Minimum number of required seconds in silence to cut it out.  
`--spaces-on-edges`, `-s`: Leaves some space on the edges of silence cut.  

## Examples
The simplest way you can run the program
```
py __main__.py -i input_path -o output_path -d_ default_img_path -a_ active_img_path
```
Or add some parameter  
```
py __main__.py -i input_path -o output_path -d_ default_img_path -a_ active_img_path -x 5 -w_ 1920 -h_ 1080 --fps 60
```
