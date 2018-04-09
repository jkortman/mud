import unittest
import mud

class TestSpan(unittest.TestCase):
    def test(self):
        events = [
            (mud.Note('C4', 1), mud.Time(0)),
            (mud.Note('G5', 1), mud.Time(0)),
            (mud.Rest(      1), mud.Time(1)),
            (mud.Note('C4', 2), mud.Time(2)),
            (mud.Note('A4', 2), mud.Time(2)),
        ]
        span = mud.Span(events, length=4, offset=4)
        self.assertAlmostEqual(span.length().in_beats(), 4.0)
        self.assertAlmostEqual(span.offset().in_beats(), 4.0)

        for i, (event, time) in enumerate(events):
            self.assertEqual(span[i], mud.Event(event, time))

    def test_concat(self):
        span_a = mud.Span([
            (mud.Note('C4', 1), mud.Time(0)),
            (mud.Note('G5', 1), mud.Time(0)),
        ])
        span_b = mud.Span([
            (mud.Rest(      1), mud.Time(0)),
            (mud.Note('C4', 2), mud.Time(1)),
            (mud.Note('A4', 2), mud.Time(1)),
        ])
        events_target = [
            (mud.Note('C4', 1), mud.Time(0)),
            (mud.Note('G5', 1), mud.Time(0)),
            (mud.Rest(      1), mud.Time(1)),
            (mud.Note('C4', 2), mud.Time(2)),
            (mud.Note('A4', 2), mud.Time(2)),
        ]

        span_concat = mud.Span.concat(span_a, span_b)
        self.assertAlmostEqual(span_concat.length().in_beats(), 4.0)
        self.assertAlmostEqual(span_concat.offset().in_beats(), 0.0)
        for i, (event, time) in enumerate(events_target):
            self.assertEqual(span_concat[i], mud.Event(event, time))
    
    @unittest.skip("incomplete")
    def test_overlay(self):
        span_a = mud.Span([
            (mud.Note('C4', 1), mud.Time(0)),
            (mud.Note('G5', 1), mud.Time(1)),
        ])
        span_b = mud.Span([
            (mud.Note('A4', 1), mud.Time(0)),
            (mud.Note('C4', 1), mud.Time(1)),
        ])
        events_target = [
            (mud.Note('C4', 1), mud.Time(0)),
            (mud.Note('A4', 1), mud.Time(0)),
            (mud.Note('G5', 1), mud.Time(1)),
            (mud.Note('C4', 1), mud.Time(1)),
        ]
