import pyactr as actr
import contextlib

# next goal is to include ISI

# Configuration with termination signal
letters = ["B", " ", "C", " ", "A", " ", "D", " ", "E", " ", "A", " ", "F", " ", "DONE"]
letter_duration = 0.3
ISI = 1.3
screen_center = (320, 185)

# Create environment
environ = actr.Environment(focus_position=screen_center)

# Initialize model
m = actr.ACTRModel(environment=environ, subsymbolic=True)

# Declare chunk types
actr.chunktype("read", "state, finished")
actr.chunktype("image", "img")

# Initialize buffers with termination flag
m.goal.add(actr.chunkstring(name="reading", string="""
    isa     read
    state   start
    finished no"""))

g2 = m.set_goal("g2")
g2.delay = 0.2

m.productionstring(name="encode_letter", string="""
    =g>
        isa     read
        state   start
        finished no
    =visual>
        isa     _visual
        value  =letter
        value ~"DONE"
    ==>
    =g>
        isa     read
        state   processing
        finished no
    +g2>
        isa     image
        img     =letter""")

m.productionstring(name="respond_to_A", string="""
    =g>
        isa     read
        state   processing
        finished no
    =g2>
        isa     image
        img     "A"
    ?manual>
        state   free
    ==>
    =g>
        isa     read
        state   done
        finished no
    +manual>
        isa     _manual
        cmd     press_key
        key     "1" """)

m.productionstring(name="ignore_non_A", string="""
    =g>
        isa     read
        state   processing
        finished no
    =g2>
        isa     image
        img     =letter
    ?manual>
        state   free
    ==>
    =g>
        isa     read
        state   done
        finished no""")

m.productionstring(name="reset_goal", string="""
    =g>
        isa     read
        state   done
        finished no
    ==>
    =g>
        isa     read
        state   start
        finished no""")

# termination production rules
m.productionstring(name="detect_finish", string="""
    =g>
        isa read
        state None
        finished no
    =visual>
        isa     _visual
        value   "DONE"
    ==>
    =g>
        isa     read
        state None
        finished yes""")

m.productionstring(name="terminate", string="""
    =g>
        isa     read
        state None
        finished yes
    ==>
    ~g>""")

# Create stimuli with termination signal
stimuli = []
for i, letter in enumerate(letters):
    key = f"stimulus{i}-0time"
    stimuli.append({key: {"text": letter, "position": screen_center}})

if __name__ == "__main__":
    sim = m.simulation(
        realtime=True,
        environment_process=environ.environment_process,
        stimuli=stimuli,
        triggers=letters,
        times=letter_duration
    )
    # Create output file
    with open('actr_trace.txt', 'w') as f:
        with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            # Run simulation
            sim.run(letter_duration)