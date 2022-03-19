#!/usr/bin/python

import sys
import re

try:
    from pathlib import Path
    from colorama import Fore, Style
    import colorama
    from PIL import Image, UnidentifiedImageError
    import typer
except ModuleNotFoundError as e:
    missing_module = re.findall(r"'(.+?)'", str(e))[0]
    print(f'[ ERROR ] Missing module \'{missing_module}\'')
    sys.exit(1)

app = typer.Typer(add_completion=False)
colorama.init()

# Main command of the app
@app.callback(invoke_without_command=True)
def ascii(
    image_path: Path = typer.Argument(..., help='The path to the image to convert', metavar='[path_to_image]'),
    invert: bool = typer.Option(False, '-i', '--invert', help='Invert all the image pixels rgb'),
    output: Path = typer.Option('', '-o', '--output', help='Put the final ascii too a external file', metavar='[path_to_output]'),
    read: bool = typer.Option(False, '-r', '--read', help='If the path is a text file this will read it and print it'),
    size: float = typer.Option(50, '-s', '--size', help='Change the percentage of reduction of the image (Don\'t put % in the percentage)', metavar='percentage')):
    """
    ascli is a little cli program that allows you to convert a image to a text ascii art.
    Made by ZKutury.
    """
    
    # Check if image exist and is in the correct format
    if not image_path.exists():
        error(f'The path \'{image_path}\' doesn\'t exist!')
    
    if not image_path.is_file():
        error(f'The path \'{image_path}\' isn\'t a file')
    
    # If the user select the read mode all the code below isn't executed
    try:
        if read:
            with open(image_path, 'r') as file:
                typer.echo(file.read())
                raise typer.Exit(code=1)
    except UnicodeDecodeError as e:
        error('Invalid file type')
    except Exception as e:
        error(f'An unexpected error \'{e}\' has occurred')

    # Checking if the custom resize number is correct and convert it from percentage to decimal
    if size < 1 or size > 100:
        error('Invalid size number, please use a number between 1 and 100')

    density, width = image(image_path, size/100)
    image_str = associate(density, invert)
    print_(image_str, width, output)

def image(path: Path, size: float):
    # Get the density of the image with the average of the rgb
    # Opening it with PIL and making the calcs
    with Image.open(path.absolute().as_posix()) as image:
        fixed_image = image.convert("RGB").resize((int(image.width * size), int(image.height * size)), Image.BILINEAR)
        rgb = fixed_image.load()
        density = []
        
        for x in range(int(fixed_image.width)):
            for y in range(int(fixed_image.height)):
                density.append((rgb[y,x][0]+rgb[y,x][1]+rgb[y,x][2])/3)
        
        return density, fixed_image.width

def associate(density: list[int], invert):
    # Generating a dict with all the associations leter to density
    # And put all into a string
    # Get a density dict
    density_dict = {}
    order = -1
    
    if invert:
        order = 1
        
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

def print_(image_str: str, width: int, output: Path):
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
        warning(f'The directories too the file doesn\'t exist. You want to create them? (Y/n) {Fore.BLUE+Style.BRIGHT}->{Style.RESET_ALL} ', end='')
        answer = input().upper()
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

def warning(message: str = 'Something is wrong', **kwars):
    # Standard warning message
    print(f'{Fore.YELLOW+Style.BRIGHT}[ WARNING ]{Style.RESET_ALL} {message}', **kwars)

def success(message: str = 'All is fine'):
    # Standard success message
    typer.echo(f'{Fore.GREEN+Style.BRIGHT}[ SUCCESS ]{Style.RESET_ALL} {message}')

# Start the app
if __name__ == '__main__':
    try:
        app()
    except UnidentifiedImageError:
        typer.echo(f'{Fore.RED+Style.BRIGHT}[ ERROR ]{Style.RESET_ALL} Invalid file type!', err=True)
    except PermissionError:
        typer.echo(f'{Fore.RED+Style.BRIGHT}[ ERROR ]{Style.RESET_ALL} Permission to write to output denied', err=True)
    except Exception as e:
        typer.echo(f'{Fore.RED+Style.BRIGHT}[ ERROR ]{Style.RESET_ALL} An unexpected error \'{e}\' has occurred', err=True)