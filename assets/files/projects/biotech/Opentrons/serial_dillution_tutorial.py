from opentrons import protocol_api

metadata = {
    "protocolName": "Serial Dilution Tutorial",
    "description": """This protocol is the outcome of following the
                   Python Protocol API Tutorial located at
                   https://docs.opentrons.com/v2/tutorial.html. It takes a
                   solution and progressively dilutes it by transferring it
                   stepwise across a plate.""",
    "author": "Xavier"
}

requirements = {"robotType": "Flex", "apiLevel": "2.22"}


def run(protocol: protocol_api):

    # Define the labware
    tips = protocol.load_labware("opentrons_flex_96_tiprack_200ul","D1")
    reservoir = protocol.load_labware("nest_12_reservoir_15ml", "D2")
    plate = protocol.load_labware("nest_96_wellplate_200ul_flat", "D3")

    # Define the liquids
    SolventWater = protocol.define_liquid(
        name="water",
        description="Non colored water for demo",
        display_color="#FFFFFF",
        )
    
    BlueWater = protocol.define_liquid(
        name="Blue water",
        description="Blue colored water for demo",
        display_color="#0000FF",
        )

    # Load the reservoir
    reservoir.load_liquid(
        wells = ["A1"],
        volume = 14000, # we expect uL
        liquid = SolventWater
        )
    
    reservoir.load_liquid(
        wells = ["A2"],
        volume = 14000, # we expect uL
        liquid = BlueWater
        )
    
    # Define the trash container
    trash = protocol.load_trash_bin("A3")


    # Define the pipette     
    left_pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=[tips])

    # fill all the plate with 100 uL of solvant    
    left_pipette.transfer(100, reservoir["A1"], plate.wells())

    # start the serial dillution


    for i in range(8):
        row = plate.rows()[i] # called the i-th row
        # 2nd phase
        left_pipette.transfer(100, # take 100 uL
                            reservoir['A2'], # from the second position of reservoir
                            row[0], # put them in the first well of the row
                            mix_after=(3, 50) # mix 3 times with 50 uL after dispensing
                            )
        
        # 3rd phase
        left_pipette.transfer(100, # take 100 uL
                            row[:11], # from all the wells but the last
                            row[1:], # put to all the wells but the first
                            mix_after=(3, 50) # mix 3 times with 50 uL after dispensing
                            )