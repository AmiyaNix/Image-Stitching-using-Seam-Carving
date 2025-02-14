import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def load_image(path):
    img = cv2.imread(path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Hide Tkinter root window (we only need the file dialog)
Tk().withdraw()

# Ask the user to select the first image
print("Please select the first image")
image1_path = askopenfilename(title="Select the first image", filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])

# Ask the user to select the second image
print("Please select the second image")
image2_path = askopenfilename(title="Select the second image", filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])

# Load the images using the selected paths
image1 = load_image(image1_path)
image2 = load_image(image2_path)

# Show the selected images
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(image1)
plt.title("Image 1")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(image2)
plt.title("Image 2")
plt.axis("off")

plt.show()


def resize_to_same_height(img1, img2):
    h1, w1, _ = img1.shape
    h2, w2, _ = img2.shape
    target_height = min(h1, h2)

    img1_resized = cv2.resize(img1, (int(w1 * target_height / h1), target_height))
    img2_resized = cv2.resize(img2, (int(w2 * target_height / h2), target_height))

    return img1_resized, img2_resized

# Resize images
image1, image2 = resize_to_same_height(image1, image2)

# Show resized images
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(image1)
plt.title("Resized Image 1")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(image2)
plt.title("Resized Image 2")
plt.axis("off")

plt.show()


def resize_to_same_height(img1, img2):
    h1, w1, _ = img1.shape
    h2, w2, _ = img2.shape
    target_height = min(h1, h2)

    img1_resized = cv2.resize(img1, (int(w1 * target_height / h1), target_height))
    img2_resized = cv2.resize(img2, (int(w2 * target_height / h2), target_height))

    return img1_resized, img2_resized

# Resize images
image1, image2 = resize_to_same_height(image1, image2)

# Show resized images
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(image1)
plt.title("Resized Image 1")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(image2)
plt.title("Resized Image 2")
plt.axis("off")

plt.show()


def find_overlap_width(img1, img2, overlap_ratio=0.2):
    overlap_width = int(min(img1.shape[1], img2.shape[1]) * overlap_ratio)
    return overlap_width

# Define overlap width
overlap_width = find_overlap_width(image1, image2)

# Crop overlapping regions
overlap_region1 = image1[:, -overlap_width:]  # Right side of image1
overlap_region2 = image2[:, :overlap_width]   # Left side of image2

# Display Overlapping Regions
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(overlap_region1)
plt.title("Overlap from Image 1")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(overlap_region2)
plt.title("Overlap from Image 2")
plt.axis("off")

plt.show()



def compute_energy(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    energy = np.abs(sobel_x) + np.abs(sobel_y)
    return energy.astype(np.uint8)

# Compute energy for the overlap region
energy_overlap1 = compute_energy(overlap_region1)
energy_overlap2 = compute_energy(overlap_region2)

# Show Energy Maps
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(energy_overlap1, cmap='gray')
plt.title("Energy Map of Overlap (Image 1)")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(energy_overlap2, cmap='gray')
plt.title("Energy Map of Overlap (Image 2)")
plt.axis("off")

plt.show()



def find_vertical_seam(energy):
    h, w = energy.shape
    dp = energy.copy()

    # Dynamic programming to find the minimal energy seam
    for i in range(1, h):
        for j in range(w):
            if j == 0:
                dp[i, j] += min(dp[i-1, j], dp[i-1, j+1])
            elif j == w-1:
                dp[i, j] += min(dp[i-1, j-1], dp[i-1, j])
            else:
                dp[i, j] += min(dp[i-1, j-1], dp[i-1, j], dp[i-1, j+1])

    # Backtrack to find seam path
    seam = []
    j = np.argmin(dp[-1])
    seam.append(j)

    for i in range(h-2, -1, -1):
        if j == 0:
            j = np.argmin(dp[i, j:j+2])
        elif j == w-1:
            j = j-1 + np.argmin(dp[i, j-1:j+1])
        else:
            j = j-1 + np.argmin(dp[i, j-1:j+2])
        seam.append(j)

    return np.array(seam[::-1])

# Find seam for blending
seam = find_vertical_seam(energy_overlap1)

# Show Seam
seam_image = overlap_region1.copy()
for i in range(overlap_region1.shape[0]):
    seam_image[i, seam[i]] = [255, 0, 0]  # Highlight seam in red

plt.imshow(seam_image)
plt.title("Optimal Seam for Merging")
plt.axis("off")
plt.show()



def remove_seam(image, seam):
    h, w = image.shape[:2]
    return np.array([np.delete(image[i], seam[i], axis=0) for i in range(h)])

# Remove seam from overlap
overlap_region1_carved = remove_seam(overlap_region1, seam)

# Blend images
blended_overlap = (overlap_region1_carved * 0.5 + overlap_region2[:, :overlap_region1_carved.shape[1]] * 0.5).astype(np.uint8)

# Concatenate final panorama
panorama = np.hstack([image1[:, :-overlap_width], blended_overlap, image2[:, overlap_width:]])

# Show Panorama
plt.imshow(panorama)
plt.title("Seam Carved Panorama")
plt.axis("off")
plt.show()

# Save final output
plt.imsave("panorama_seam_carving.png", panorama)
