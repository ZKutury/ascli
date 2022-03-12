#!/usr/bin/python

#+ Fix Resize (not resize, interpole)
#+ Error handler of: Wrong file type, output non writable, already exist and dependencies, file incorrect read
#+ Help text
#+ Read -r --read
#+ Change the question to one line

from pathlib import Path
from colorama import Fore, Style
#from rgbprint.rgbprint import _print as print #! Change this shit
import colorama
from PIL import Image
import typer

app = typer.Typer(add_completion=False)
colorama.init()

# Main command of the app
@app.callback(invoke_without_command=True)
def ascii(image_path: Path, invert: bool = typer.Option(False, '-i', '--invert'), output: Path = typer.Option('', '-o', '--output'), color: str = typer.Option('#FFFFFF', '-c', '--color'), read: bool = typer.Option(False, '-r', '--read')):
    
    # Check if image exist and is in the correct format
    if not image_path.exists():
        error(f'The path \'{image_path}\' doesn\'t exist!')
    
    if not image_path.is_file():
        error(f'The path \'{image_path}\' isn\'t a file')
    
    try:
        if read:
            with open(image_path, 'r') as file:
                typer.echo(file.read())
                return
    except Exception as e:
        error(e)

    density, width = image(image_path)
    image_str = associate(density, invert)
    print_(image_str, width, output, color)

def image(path: Path):
    # Get the density of the image with the average of the rgb
    # Opening it with PIL and making the calcs
    with Image.open(path.absolute().as_posix()) as image:
        #! The resize tilt the image
        fixed_image = image#?.resize((int(image.width*0.9999999999999999), int(image.height*0.9999999999999999)), Image.ANTIALIAS)
        rgb = fixed_image.load()
        density = []
        
        for x in range(int(fixed_image.width)):
            for y in range(int(fixed_image.height)):
                density.append((rgb[y,x][0]+rgb[y,x][1]+rgb[y,x][2])/3)
        
        return density, image.width

def associate(density: list, invert):
    # Generating a dict with all the associations leter to density
    # And put all into a string
    # Get a density dict
    density_dict = {}
    if invert:
        order = 1
    else:
        order = -1
    letters = "$@B%8&WM\#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\'^`'. "[::order]
    chars_per_letter = int(255/len(letters))
    numbers = list(range(0,256))
    for i, letter in enumerate(letters):
        for o in numbers[i*chars_per_letter:i*chars_per_letter+3]:
            density_dict[o] = letter
    
    # Get the full string
    densified_letters = ''
    for i in density:
        i = int(i)
        if i > 212:
            i = 212
        densified_letters += density_dict[i]
        
    return densified_letters

def print_(image_str: str, width: int, output: Path, color: str):
    # Print the output and save it if output path exist
    lines = []
    for i in range(0, len(image_str), width):
        lines.append(image_str[i:i+width])
    spaced_output = '\n'.join(lines)
    print(spaced_output, end='\n\n') # The final output
    
    # If the user request it the app put the output too a external file
    save_output(spaced_output, output)

def save_output(spaced_output, output):
    # Put the output too a external file if the user request it
    if output == Path('.'):
        return
    
    if not output.parents[0].exists():
        # Check if the parent folders exist and ask too create them
        warning('The directories too the file doesn\'t exist. You want to create them? (Y/n)')
        answer = input(f'{Fore.BLUE+Style.BRIGHT}[ INPUT ]{Style.RESET_ALL} -> ').upper()
        if answer == 'Y' or '\n':
            output.parents[0].mkdir(parents=True, exist_ok=True)
            success('Created the missing folders')
        else:
            error('Path not available')
            
    # Create and write in the file itself
    output.touch()
    with open(output, 'w') as file:
        file.write(spaced_output)
    success(f'Output file created at {output}')

def error(message: str = 'An unexpected error has occurred'):
    # Standard error message
    typer.echo(f'{Fore.RED+Style.BRIGHT}[ ERROR ]{Style.RESET_ALL} {message}', err=True)
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