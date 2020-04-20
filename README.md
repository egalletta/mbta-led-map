# MBTA LED Map

A simple and fast way to know when your train will arrive.

![image](https://github.com/egalletta/mbta-led-map/blob/master/docs/light.gif "Map")

[Full Video Here](https://github.com/egalletta/mbta-led-map/blob/master/docs/video.MOV)


<!-- vim-markdown-toc GFM -->

* [Background](#background)
* [Data Used](#data-used)
* [How it Works](#how-it-works)
                * [Hardware](#hardware)
                * [Software](#software)
* [Value](#value)
* [Next Steps](#next-steps)

<!-- vim-markdown-toc -->
## Background

My product modifies the existing MBTA full subway map by incorporating LED
lights into the stops on the map that update in real time with the true vehicle
positions of the trains. I saw a need for a solution like this through my own
experience riding the T; I noticed that at some of the larger transfer stations
(such as Government Center or Park Street) many passengers would make a mad dash
out of the door of their train, often elbowing others on their way, in order to
hurry to the next platform in fear of potentially missing their next train if
they had not rushed. Additionally, Northeastern University (where I attend
school) is equidistant between both Ruggles and the Northeastern Green Line
stops, and almost every time I needed to go Downtown I've pulled out my phone
and loaded up a MBTA-tracking app to see which line would arrive first. My
product aims to help in both of these situations: riders at larger transfer
stations could glance at an improved map as they are leaving their train to see
if sprinting up the stairs would be really worth it, as could I as I am leaving
my apartment to see which line I should go to.


I had two primary goals when designing my product, which I believe that I have
accomplished: being more 'efficient' than the currently existing solutions
(faster while communicating more information) and being accessible to as many
riders of the T as I could be. The two main current solutions that I had
identified were the countdown clocks already in T stations and smartphone apps
that show the T data in realtime. My two greatest issues with these solutions
came down to my efficiency and accessibility goals: countdown clocks only show
the next two trains for a given line, and smartphone apps are only useful to
riders that have smartphones with good enough reception to work down in the
depths of the subway tunnels. My map fulfills both of these goals of mine, as it
shows all of the train positions by using the same map that every rider is sure
to have seem before and be familiar with, and does not assume any requirements
from the rider- the information is displayed for anyone who can physically see
it.


## Data Used

In order to determine where the train's positions were, I needed to use the MBTA
API. MBTA's API allows for limited use without a key, however, since I was going
to need to make more than the allotted 20 requests per minute in order to update
the trains, I needed to apply for a key. This process was very simple to do, and
after applying for a key on their developer site
[here](https://api-v3.mbta.com/), I was ready to start looking at some data.

MBTA's v3 API has some good
[documentation](https://api-v3.mbta.com/docs/swagger), but I found that I had to
do some work myself in order to make their data usable for me. I primarily used
the `/vehicles` request in order to get my data, with some help from a `/stops`
request at the beginning as well. I noticed that while a `/vehicles` request
for a specific subway line showed a _ton_ of information about the train, but
not quite the information I needed. Each vehicle returned by `/vehciles`
included its exact position in latitude and longitude, name, id, direction, and
its "status." The only information provided about the stop it was near was its
`current_stop_sequence`, which I could not seem to decipher myself as it did not
appear to be in any particular order, and its `stop_id`, which, while note
perfect, at least gave me something that could eventually turn into a stop's
name.

After digging through some more
[documentation](https://developers.google.com/transit/gtfs-realtime/reference#enum-vehiclestopstatus)
and looking at a few examples, I found one other aspect of a `/vehciles` 
request that would be especially handy for me: a vehicle's `current_status` was
meant to be "placed in front of" its `stop_id,` and, due to the way each status
is phrased, a vehicle's `stop_id` would always be a stop that a train is _at_ or
is _approaching_, never a stop that a train just left. While this may seem like
a minor detail, it actually has somewhat of a large, positive impact on the way
that this data will eventually get displayed: if a stop is lit up on my map, it
would (theoretically) mean that if someone was standing on the platform of a
station that is lit up, they would be able to still board the train. This would
be important for the user, as they would not experience any "false positives"
this way where a station is lit up but the train had already passed.

## How it Works

_TL;DR Raspberry Pi asks MBTA where trains are, translates their `stop_id` into an
actual stop, and then tells a bunch of Arduinos to tell the right LEDs to light
up_

#### Hardware

In order to put all of this together, I used a combination of a Raspberry Pi 4
and four different Sparkfun Redboards (which are pretty much just Arduino Unos)
that I had lying around. While this project could probably have just used two or
even one of these boards, I started using one for each line in order to see
initial progress better, and stuck with it since. One of these Arduinos is
responsible for updating the LCD display on the front of the map, while the
other 3 are used to light up the LEDs: the Orange and Blue lines share one
Arduino, while the Red and Green line have their own. Since most of the lines
have many stops, more than the Arduino has pins, I used 8-bit shift registers in
order to expand the amount of effective digital output pins I could used.
Essentially, they allow just 3 pins on the Arduino to be used as many indivudual
outputs- for the Green Line I was able to use as many as 72. Each register has 8
bits that it can output, and they can be daisy-chained together to allow for
more. Here is a circuit diagram outlining how I put these together with my LEDs: 

![image](https://github.com/egalletta/mbta-led-map/blob/master/docs/circut.png "Circut")

While this only shows two shift registers chained together, many more can be
linked together as well.


For the LCD display, I used a 20x4 display that I found from an old project, and
followed [this](https://www.arduino.cc/en/Tutorial/LiquidCrystalSerialDisplay)
tutorial on how to wire it up and used the example code provided to display the
text.

In order to control all of these Arduinos, I used a Raspberry Pi 4 to
communicate with them via serial. While the Pi 4 might be overkill and I
probably don't need that much power to run this, I had it already and it runs
Linux and was painless to move code written on my laptop over to it.
Alternatively, any other computer could be used in place of the Pi as well.

The rest of the 'hardware' used isn't really electronics, but rather making
these lights look nice. I used an thick piece of cardboard about the size of the
MBTA maps found in subway stations, and printed out the MBTA subway map to put
on top of it. Then, I drilled out a hole in each stop, so that I could put an
LED through them and connect them to the breadboard on the backside of the
cardboard; soldering each LED individually took longer than I would like to
admit.


#### Software

On the software side of things, a Python script,
[mbta-controller.py](mbta-controller.py), is in charge of communicating with the
MBTA API and translating its information into something that the Arduinos can
easily work with. The way that it does this is (relatively) simple:

- Get the list of vehicles from the API for the specified line
- Make a list that is the same length of the line
- For each of these vehicles:
    - Make sure it is going the direction needed
    - Look up the vehicle's `stop_id` in a dictionary to get its stop name
    - Look up the stop's name in another dictionary to see what pin its LED is,
      and set this index in the list we just made to be a "1" instead of a "0"

Once this is done, a string is produced that looks like `"1000010000100100"`,
where a 1 represents a train at that station. This string, with a character
prepended to it that represents what line it is for, is then send over to
that line's Arduino, which then uses that string to update its LEDs. 
  

Additionally, a few arguments can be specified when running `mbta-controller.py`
as well. Its help page is listed here:

```{bash}
usage: mbta_controller.py [-h] [--north] [--south] [--red] [--green]
                          [--orange] [--blue] [--debug]

Options for trains:

optional arguments:
  -h, --help    show this help message and exit
  --north, -n   Display trains going northbound
  --south, -s   Display trains going southbound
  --red, -r     Show red line trains
  --green, -g   Show green line trains
  --orange, -o  Show orange line trains
  --blue, -b    Show blue line trains
  --debug, -d   Enable stop output to STDOUT of host

```
In order to run the program, the user just needs to run `./mbta-controller.py`,
followed by the arguments desired. These arguments can be all combined, so if
the user wanted to see Blue Line trains going Northbound, they would run
`./mbta-controller --north --blue`, and if a user wanted to see Orange and Red
Line trains and alternate between both North and Southbound, they could run
`./mbta-controller.py -nsor`.

## Value
Originally, my goal for this project were to help riders of the MBTA figure out
where the trains currently are both more efficiently and more accessibly than
the currently available solutions. After seeing my map come to life, I believe
that it could fulfil both of these ambitions. Individuals could mount my map on
their wall, and run the program with the configurations that they would need
when leaving their house or apartment; for example, someone living in Assembly
Square commuting to East Boston could use `./mbta-controller.py -nsob` to see
North and South trains on both the Orange and Blue Lines. Likewise, this map
could be displayed in a station like North Station on the platform serving both
Orange and Green Line trains heading South/Westbound by using
`./mbta-controller.py -sog`. This would allow people heading to destinations
served by either of these lines (like myself heading back to Northeastern) to
determine which line will come first, and choose to wait at that platform,
instead of rushing over to the other side if they notice a train coming.

## Next Steps

Displaying where the trains are, while arguably the most important and useful,
is not where this project stops. I found _sooooo_ much useful information in the
MBTA API that I could further add to this LED Map platform. For example, knowing
how (un)reliable the T can be, I plan to add notifications about delays and
detours to my map as well. If there is a disabled train at Malden Center that is
causing delays, I would want passengers to know that information as easily as
possible so that they be more informed on their commute and perhaps seek an
alternative route. I plan to add this implementation by using the MBTA API to
monitor for service alerts, and then flash LEDs either at a specific station if
there is a local problem, or the lights on a larger segment or line as a whole
if there is a more widespread issue. By using this instant, visual feedback
along with the other information already displayed, I hope to bring an overall
improvement to the hectic commutes that riders face on the MBTA.   
  











          

























