"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import arcade
import random
import yaml

from libs.player import PlayerCharacter
from libs.room import Room
from utils.config import ConfigFile

from math import floor, ceil


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, configurations):
        
        self.configurations = ConfigFile(configurations)
        self.player_infos = self.configurations.general.player
        self.map_infos = self.configurations.general.map
        # Variables that will hold sprite lists
        self.player_list = None
        # Sprite lists
        self.current_room = 0

        # Set up the player
        self.rooms = None
        self.score = 0
        self.sprite_size = int(self.configurations.general.sprite_native_size * self.configurations.general.sprite_scaling_room)
        self.screen_width = self.sprite_size * self.configurations.general.screen_width
        self.screen_height = self.sprite_size * self.configurations.general.screen_height

        super().__init__(self.screen_width, self.screen_height, self.configurations.general.screen_title)

        # Don't show the mouse cursor
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.AMAZON)


    def setup(self):
        # Create your sprites and sprite lists here
        # Sprite lists
        self.player_list = arcade.SpriteList()

        self.player = PlayerCharacter(self.screen_width, self.screen_height, self.player_infos.sprite_scaling_player)
        # Load textures of the sprite
        if 'textures' not in self.player_infos.data:
            raise Exception('No textures for the player found')
        for texture in self.player_infos.textures:
            self.player.load_sprite(texture['file'], 
                                    texture['name'],
                                    texture['nframes'], 
                                    texture['frame'], 
                                    texture['width'], 
                                    texture['height'],
                                    texture['offset'])

        self.player.textures = self.player.textures + self.player.idle_texture

        # self.player.textures = []
        # for i in range(9):
        #     self.player.textures.append(arcade.load_texture("assets/sprites/walk_front.png", x=16+i*64, y=0, width=40, height=56))
        self.player.textures.append(self.player.idle_texture)
        self.coin_list = arcade.SpriteList()

        # Set up the player
        self.player.setCoordenates(self.screen_width // 2, self.screen_height // 2)
        self.player_list.append(self.player)

        # Create the rooms
        # Our list of rooms
        self.rooms = []
        # Create the rooms. Extend the pattern for each room.
        i = 0
        for room in self.map_infos.rooms:
            new_room = Room(self.screen_width, self.screen_height, self.sprite_size, self.configurations.general.sprite_scaling_room)
            new_room.setup(room['walls'], room['background'])
            new_room.id = i
            if 'wall_at' in room:
                for wall in room['wall_at']:
                    new_room.addWall(int(wall.split(',')[0]), int(wall.split(',')[1]))

            if 'connect_east' in room:
                new_room.removeWall(13, floor((self.map_infos.grids_height-1) / 2))
                new_room.removeWall(13, ceil((self.map_infos.grids_height-1) / 2))
                new_room.setNearRooms('east', room['connect_east'])
            if 'connect_west' in room:
                new_room.removeWall(0, floor((self.map_infos.grids_height-1) / 2))
                new_room.removeWall(0, ceil((self.map_infos.grids_height-1) / 2))
                new_room.setNearRooms('west', room['connect_west'])
            if 'connect_south' in room:
                new_room.removeWall(floor((self.map_infos.grids_width-1) / 2), 0)
                new_room.removeWall(ceil((self.map_infos.grids_width-1) / 2), 0)
                new_room.setNearRooms('south', room['connect_south'])
            if 'connect_north' in room:
                new_room.removeWall(floor((self.map_infos.grids_width-1) / 2), 9)
                new_room.removeWall(ceil((self.map_infos.grids_width-1) / 2), 9)
                new_room.setNearRooms('north', room['connect_north'])
            self.rooms.append(new_room)
            i+=1

        # Create the treasures
        for treasure in self.map_infos.treasure:
            # Create the coin instance
            # Coin image from kenney.nl
            coin = arcade.Sprite(treasure['image'],
                                 treasure['scaling'])
            # Position the coin
            coin.center_x = random.randrange(self.sprite_size, self.screen_width-self.sprite_size, 1)
            coin.center_y = random.randrange(self.sprite_size, self.screen_height-self.sprite_size, 1)
            # Add the coin to the lists
            self.rooms[treasure['location']].treasures_list.append(coin)
        
        self.current_room = 0
        # Create a physics engine for this room
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.rooms[self.current_room].wall_list)



    def on_draw(self):
        """
        Render the screen.
        """
        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        # Call draw() on all your sprite lists below
        """ Draw everything """
        arcade.start_render()
        # Draw the background texture
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            self.screen_width, self.screen_height,
                                            self.rooms[self.current_room].background)

        # Draw all the walls in this room
        self.rooms[self.current_room].wall_list.draw()
        self.rooms[self.current_room].treasures_list.draw()
        self.player_list.draw()

        # Put the text on the screen.
        output = f"Score: {self.score} \n Position: {self.player.center_x} {self.player.center_y}"
        arcade.draw_text(output, 10, 20, arcade.color.BLACK, 14)


    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        """ Movement and game logic """
        self.physics_engine.update()
        # Call update on all sprites 
        self.player_list.update()
        self.player_list.update_animation()

        # Generate a list of all sprites that collided with the player.
        treasure_hit_list = arcade.check_for_collision_with_list(self.player, self.rooms[self.current_room].treasures_list)

        # Loop through each colliding sprite, remove it, and add to the score.
        for treasure in treasure_hit_list:
            treasure.remove_from_sprite_lists()
            self.score += 1

        # Do some logic here to figure out what room we are in, and if we need to go
        # to a different room.
        if self.player.center_x + self.player.lateralMargin >= self.screen_width:
            self.current_room = self.rooms[self.current_room].getNearRooms('east')
            # if self.current_room == 0:
            #     self.current_room = 1
            # elif self.current_room == 2:
            #     self.current_room = 3            
            self.player.center_x = self.sprite_size + self.player.lateralMargin
            self.updateRoom(self.current_room)
        elif self.player.center_x - self.player.lateralMargin <= 0:
            # if self.current_room == 1:
            #     self.current_room = 0
            # elif self.current_room == 3:
            #     self.current_room = 2
            self.current_room = self.rooms[self.current_room].getNearRooms('west')
            self.player.center_x = self.screen_width - self.sprite_size - self.player.lateralMargin
            self.updateRoom(self.current_room)
        elif self.player.center_y - self.player.verticalMargin <= 0:
            # if self.current_room == 0:
            #     self.current_room = 2
            # elif self.current_room == 1:
            #     self.current_room = 3
            self.current_room = self.rooms[self.current_room].getNearRooms('south')
            self.player.center_y = self.screen_height - self.sprite_size - self.player.verticalMargin
            self.updateRoom(self.current_room)
        elif self.player.center_y + self.player.verticalMargin >= self.screen_height:
            # if self.current_room == 2:
            #     self.current_room = 0
            # elif self.current_room == 3:
            #     self.current_room = 1
            self.current_room = self.rooms[self.current_room].getNearRooms('north')
            self.player.center_y = self.sprite_size + self.player.verticalMargin
            self.updateRoom(self.current_room)

        
    def updateRoom(self, room):    
        self.physics_engine = arcade.PhysicsEngineSimple(self.player,
                                                             self.rooms[room].wall_list)
    

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if key == arcade.key.UP:
            self.player.change_y = self.player_infos.movement_speed
        elif key == arcade.key.DOWN:
            self.player.change_y = -self.player_infos.movement_speed
        elif key == arcade.key.LEFT:
            self.player.change_x = -self.player_infos.movement_speed
        elif key == arcade.key.RIGHT:
            self.player.change_x = self.player_infos.movement_speed


    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0



def main():
    """ Main method """
    # instantiate
    with open("assets/games/game1.yaml", 'r') as stream:
        config = yaml.safe_load(stream)
    
    configurations = ConfigFile(config)
    game = MyGame(config)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()