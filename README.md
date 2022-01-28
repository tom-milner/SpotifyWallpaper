# SpotifyWallpaper

## About

This project creates a desktop wallpaper made from a collage of your favourite Spotify tracks.

## Usage

1. First, set up a new Spotify project for SpotifyWallpaper. This can be done [here](https://developer.spotify.com/dashboard/applications).
2. Run the following command to create a file for the required environment variables:

   ```bash
   cp .env.b .env
   ```

3. Now you can fill in these variables with the values that relate to your Spotify project.
4. Install the required dependencies for the project by running:

   ```bash
   pipenv install -r requirements.txt
   ```

5. Now run the project using:
   ```bash
   pipenv run python3 Wallpaper.py
   ```
