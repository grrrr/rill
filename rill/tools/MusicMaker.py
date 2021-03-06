import abjad 
import mccartney 
import rill 

from abjadext import rmakers 

# Music Maker 
class MusicMaker(object):
    """
    Populates a staff one measure at a time
    """

    def __init__(self, staff):
        self.staff = staff

    def make_music(self, durations, denominator, divisions, pitches):
        # make rhythm with one tuplet per division
        stack = rmakers.stack(
            rmakers.talea(
                durations,
                denominator, 
                extra_counts=(0, 0, 0),
            ),
            rmakers.beam()
        )
        selection = stack(divisions)

        # attach time signature to first leaf in each tuplet
        assert len(divisions) == len(selection)
        previous_time_signature = None
        for division, tuplet in zip(divisions, selection):
            time_signature = abjad.TimeSignature(division)
            leaf = abjad.select(tuplet).leaf(0)
            if time_signature != previous_time_signature:
                abjad.attach(time_signature, leaf)
                previous_time_signature = time_signature

        # apply pitch material
        cyclic_tuple = abjad.CyclicTuple(pitches) 
        iterator = abjad.iterate(selection).logical_ties(pitched=True) # make iterator out of selection using logical ties as virtual measures
        iterator = enumerate(iterator) # makes enum out of iterator  
        for index, logical_tie in iterator:
            pitch = cyclic_tuple[index]
            for old_leaf in logical_tie:
                if isinstance(pitch, int):
                    old_leaf.written_pitch = pitch
                elif isinstance(pitch, list):
                    new_leaf = abjad.Chord(pitch, old_leaf.written_duration)
                    indicators = abjad.inspect(old_leaf).indicators()
                    if indicators != None:
                        for indicator in indicators:
                            abjad.attach(indicator, new_leaf)
                    abjad.mutate(old_leaf).replace(new_leaf)
                elif isinstance(pitch, abjad.Chord):
                    new_leaf = abjad.Chord(pitch, old_leaf.written_duration)
                    indicators = abjad.inspect(old_leaf).indicators()
                    if indicators != None:
                        for indicator in indicators:
                            abjad.attach(indicator, new_leaf)
                    abjad.mutate(old_leaf).replace(new_leaf)

        # remove trivial 1:1 tuplets
        self.staff.extend(selection)
        command = rmakers.extract_trivial()
        command(selection)

