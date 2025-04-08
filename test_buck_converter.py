
import pyvisa
import usb.core
import sys


def cleanup(oscope):
    ''' Cleanup after test or on test failure '''
    # oscope.write("RECall:SETup EXTernal,\"local/SIGLENT/interim_setup.xml\"")
    # oscope.query("*OPC?")
    # oscope.write("SYSTem:REMote OFF")   # unlock oscope from receiving physical interaction
    oscope.query("*OPC?")
    oscope.close()  # close rm


def main():
    print("Running program to test buck converter...\n")

    # init USB comms
    # finds USB device that has the given vendor ID & product ID (taken from Stu's oscope)
    device_configs = usb.core.find(idVendor=0xF4EC, idProduct = 0x1017)
    device_configs.set_configuration(1)

    rm = pyvisa.ResourceManager('@py')  # use pyvisa-py for backend

    try:

        # init Stu's oscope
        oscope = rm.open_resource("USB0::0xF4EC::0x1017::SDS08A0X802909::INSTR")
        oscope.chunk_size = 20*1024*1024    # 20 Mb
        oscope.read_termination = "\n"
        oscope.write_termination = "\n"

        ''' Setup for test '''
        # lock physical interaction with oscope
        # oscope.write("SYSTem:REMote ON")
        # save oscope's current settings before changing anything
        # oscope.write("SAVE:SETup EXTernal,\"local/SIGLENT/interim_setup.xml\"")
        oscope.query("*OPC?")


        # setup channels
        for n in range(1,2):
            oscope.write(f"CHANnel{n}:COUPling DC")
            # oscope.write(f"CHANnel{n}:IMPedance ONEMeg")
            oscope.write(f"CHANnel{n}:PROBe VALue,1.00E+0") # set probe attenuation to 1x
            oscope.write(f"CHANnel{n}:SWITch ON")   # switch channel hardware on
            oscope.write(f"CHANnel{n}:VISible ON")  # show channel's waveform on screen
            oscope.write(f"CHANnel{n}:LABel ON")    # display label

        # label each channel
        oscope.write(f"CHANnel1:LABel:TEXT \"Vin\"")
        oscope.write(f"CHANnel2:LABel:TEXT \"Vout\"")
        # oscope.write(f"CHANnel3:LABel:TEXT \"Duty\"")

        oscope.query("*OPC?")   # block until all above operations complete



        ''' Now run tests 
        Hookup Vin to C1, Vout to C2, duty cycle to C3 '''
        vin_values = [12, 11, 5, 24, 27]
        # todo: then shuffle value order
        oscope.write("MEASure ON")
        oscope.write("MEASure:SIMPle:CLEar")
        # what measurement types to display on the screen
        oscope.write("MEASure:SIMPle:ITEM MAX,ON; ITEM MIN,ON; ITEM AMPL,ON; ITEM MEDIAN; ITEM DUTY")

        for val in vin_values:
            input(f"Manually change vin to {val} V & press enter")

            # change trigger to match new voltage at MOSFET gate
            
            # verify Vin change
            oscope.write("MEASure:SIMPle:SOURce C1")
            oscope.query("*OPC?")
            print(f"current channel: {oscope.query("MEASure:SIMPle:SOURce?")}")
            oscope.query("*OPC?")
            vin_max_check = oscope.query("MEASure:SIMPle:VALue? MAX")
            vin_min_check = oscope.query("MEASure:SIMPle:VALue? MIN")
            vin_ampl_check = oscope.query("MEASure:SIMPle:VALue? AMPL")
            vin_med_check = oscope.query("MEASure:SIMPle:VALue? MEDIAN")
            oscope.query("*OPC?")
            print(f"Vin:\n\tmax: {vin_max_check}\n\tmin: {vin_min_check}\n\tampl: {vin_ampl_check}\n\tmed: {vin_med_check}")

            # capture Vout on Channel 2
            oscope.write("MEASure:SIMPle:SOURce C2")
            oscope.query("*OPC?")
            print(f"current channel: {oscope.query("MEASure:SIMPle:SOURce?")}")
            oscope.query("*OPC?")
            vout_max_check = oscope.query("MEASure:SIMPle:VALue? MAX")
            vout_min_check = oscope.query("MEASure:SIMPle:VALue? MIN")
            vout_ampl_check = oscope.query("MEASure:SIMPle:VALue? AMPL")
            vout_med_check = oscope.query("MEASure:SIMPle:VALue? MEDIAN")
            oscope.query("*OPC?")
            print(f"Vout:\n\tmax: {vout_max_check}\n\tmin: {vout_min_check}\n\tampl: {vout_ampl_check}\n\tmed: {vout_med_check}")

            # # capture duty cycle on MOSFET gate
            # oscope.write("MEASure:SIMPle:SOURce C3")
            # oscope.query("*OPC?")
            # print(f"current channel: {oscope.query("MEASure:SIMPle:SOURce C1?")}")
            # oscope.query("*OPC?")
            # switching_duty = oscope.query("MEASure:SIMPle:VALue? DUTY")
            # oscope.query("*OPC?")
            # print(f"MOSFET gate (switching duty): {switching_duty}")





        # # get date & time to put in file name
        # date = oscope.query("SYSTem:DATE?") # format: yyyymmdd
        # time = oscope.query("SYSTem:TIME?") # format: hhmmss

        # # Capture oscope screen & save to PC
        # oscope.write("PRINt? PNG")
        # query_return = oscope.read_raw()

        # file_name = f"C:\\Users\\pnamu\\Documents\\SCPI\\{time[0:2]}.{time[2:4]}.{time[4:6]}_{date[4:6]}-{date[6:8]}-{date[0:4]}.png"

        # with open(file_name, 'wb') as f:   # write bytes
        #     f.write(query_return)
        #     f.flush()
        #     f.close()

    
    except KeyboardInterrupt:
        cleanup(oscope)

    except Exception as e:
        print(f"\nException {e} occured during program run")
        print(f"Terminating...")
        cleanup(oscope)
        sys.exit(-1)


    cleanup(oscope)
    print("\nProgram finished successfully")


if __name__ == '__main__':
    main()