#!/usr/bin/python

#+ Convert images to arrays of they rgb data
#+ Get the contrast of the rgb and associate to a letter
#+ Print the output
#+ Extra parameters: Invert and external output
#+ Files: Main File, Image File and Color File

from pathlib import Path
from colorama import Fore, Style
import colorama
from PIL import Image
import typer

app = typer.Typer()
colorama.init()

# Main command of the app
@app.callback(invoke_without_command=True)
def ascii(image_path: Path):
    # Check if image exist and is in the correct format
    if not image_path.exists():
        error('The path doesn\'t exist!')
    
    if not image_path.is_file():
        error('The path isn\'t a file')
        
    density, width = image(image_path)
    image_str = associate(density)
    print_(image_str, width)

def image(path: Path):
    # Get the density of the image with the average of the rgb
    # Opening it with PIL and making the calcs
    with Image.open(path.absolute().as_posix()) as image:
        #! The resize tilt the image
        fixed_image = image#.resize((int(image.width*0.9999999999999999), int(image.height*0.9999999999999999)), Image.ANTIALIAS)
        rgb = fixed_image.load()
        density = []
        
        for x in range(int(fixed_image.width)):
            for y in range(int(fixed_image.height)):
                density.append((rgb[y,x][0]+rgb[y,x][1]+rgb[y,x][2])/3)
        
        return density, image.width

def associate(density: list):
    # Generating a dict with all the associations leter to density
    # And put all into a string
    # Get a density dict
    density_dict = {}
    letters = "$@B%8&WM\#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "[::-1]
    chars_per_letter = int(255/len(letters))
    numbers = list(range(0,256))
    for i, letter in enumerate(letters):
        for o in numbers[i*chars_per_letter:i*chars_per_letter+3]:
            density_dict[o] = letter
    
    # Get the full string
    densified_letters = ""
    for i in density:
        i = int(i)
        if i > 212:
            i = 212
        densified_letters += density_dict[i]
        
    return densified_letters

def print_(image_str: str, width: int):
    lines = []
    for i in range(0, len(image_str), width):
        lines.append(image_str[i:i+width])
    print('\n'.join(lines))

def error(message: str = 'An unexpected error has occurred'):
    # Standard error message
    typer.echo(f'{Fore.RED+Style.BRIGHT}[ ERROR ]{Style.RESET_ALL} {message}')
    raise typer.Exit(code=1)

def warning(message: str = 'Something is wrong'):
    # Standard warning message
    typer.echo(f'{Fore.YELLOW+Style.BRIGHT}[ WARNING ]{Style.RESET_ALL} {message}')

def success(message: str = 'All is fine'):
    # Standard success message
    typer.echo(f'{Fore.GREEN+Style.BRIGHT}[ SUCCESS ]{Style.RESET_ALL} {message}')

# Start the app
if __name__ == '__main__':
    app()