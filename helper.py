    import base64
from moviepy.editor import *



def video_to_base64(video_path):
    with open(video_path, "rb") as video_file:
        encoded_string = base64.b64encode(video_file.read())
        return encoded_string.decode('utf-8')



def change_aspec_ratio():
    video_path = "test.mp4"
    video_clip = VideoFileClip(video_path)

    # Define the new aspect ratio
    new_aspect_ratio = (16, 9)  # Change this to your desired aspect ratio, e.g., (4, 3), (1, 1), etc.

    # Resize the video to the new aspect ratio
    video_clip_resized = video_clip.resize((1080,1920))

    # Write the resized video to a new file
    output_path = "output_video.mp4"
    video_clip_resized.write_videofile(output_path, codec="libx264")

    # Close the clips
    video_clip.close()
    video_clip_resized.close()


def resize_with_padding(video_clip, target_width, target_height):
    original_width, original_height = video_clip.size

    # Calculate the aspect ratio of the original video
    aspect_ratio = original_width / original_height

    # Calculate the aspect ratio of the target size
    target_aspect_ratio = target_width / target_height

    if aspect_ratio > target_aspect_ratio:
        # Video is wider than the target size, add horizontal padding
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
        padding_vertical = (target_height - new_height) / 2
        padding_horizontal = 0
    else:
        # Video is taller than the target size, add vertical padding
        new_width = int(target_height * aspect_ratio)
        new_height = target_height
        padding_horizontal = int (target_width - new_width) / 2
        padding_vertical = 0
        padding_horizontal = int(padding_horizontal)
        padding_vertical = int(padding_vertical)

    # Resize the video with padding
    resized_clip = video_clip.resize((new_width, new_height))
    resized_clip = resized_clip.margin(left=int(padding_horizontal), right=int(padding_horizontal), top=int(padding_vertical),bottom=int(padding_vertical), color=(0, 0, 0))

    return resized_clip



def new():
    video_path = "test.mp4"
    video_clip = VideoFileClip(video_path)

    # Define the new aspect ratio
    target_width, target_height = 1080, 1920  # Target resolution

    # Resize the video to fit within the target resolution without stretching
    resized_clip = video_clip.resize((target_width, target_height))

    # Calculate padding to maintain aspect ratio
    padding_horizontal = (target_width - resized_clip.w)
    padding_horizontal = (target_width - resized_clip.w//2)//2
    padding_vertical = (target_height - resized_clip.h)

    # Apply padding to center the resized video
    resized_clip = resized_clip.margin(left=padding_horizontal, right=padding_horizontal,
                                       top=padding_vertical, bottom=padding_vertical)

    # Write the resized video to a new file
    output_path = "output_video.mp4"
    resized_clip.write_videofile(output_path, codec="libx264")

    # Close the clips
    video_clip.close()
    resized_clip.close()



# video_path = "test.mp4"
# video_clip = VideoFileClip(video_path)
#
# # Define the new aspect ratio
# target_width, target_height = 1080, 1920  # Change these values to your desired resolution
#
# # Resize the video to the new aspect ratio with padding
# video_clip_resized = resize_with_padding(video_clip, target_width, target_height)
#
# # Write the resized video to a new file
# output_path = "output_video.mp4"
# video_clip_resized.write_videofile(output_path, codec="libx264")
#
# # Close the clips
# video_clip.close()
# video_clip_resized.close()

def crop():
    video_path = "test.mp4"
    video_clip = VideoFileClip(video_path)

    # Define the target aspect ratio
    target_width, target_height = 1080, 1080  # Target resolution

    # Calculate the aspect ratio of the original video
    original_aspect_ratio = video_clip.size[0] / video_clip.size[1]

    # Calculate the dimensions for cropping
    if original_aspect_ratio > target_width / target_height:  # Video is wider than the target
        new_height = video_clip.size[1]
        new_width = int(new_height * (target_width / target_height))
    else:  # Video is taller than the target
        new_width = video_clip.size[0]
        new_height = int(new_width * (target_height / target_width))

    # Calculate the coordinates for cropping
    x1 = (video_clip.size[0] - new_width) // 2
    y1 = (video_clip.size[1] - new_height) // 2
    x2 = x1 + new_width
    y2 = y1 + new_height

    # Crop the video to the specified region
    cropped_clip = video_clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)

    # Resize the cropped clip to the target resolution
    cropped_clip = cropped_clip.resize((target_width, target_height))

    # Write the cropped video to a new file
    output_path = "output_video.mp4"
    cropped_clip.write_videofile(output_path, codec="libx264")

    # Close the clips
    video_clip.close()
    cropped_clip.close()

