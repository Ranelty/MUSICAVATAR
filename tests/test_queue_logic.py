import unittest
from unittest.mock import patch
from musicavatar.queue_logic import PlaybackQueue


class QueueLogicTests(unittest.TestCase):
    def test_sequential_next_and_repeat(self):
        q = PlaybackQueue()
        q.replace([2,3,4])
        q.select(2,0)
        self.assertEqual(q.next_target(), (3,1,None))
        q.select(4,2)
        self.assertIsNone(q.next_target())
        self.assertEqual(q.next_target(repeat=True), (2,0,None))

    def test_shuffle_previous_is_last_heard_not_previous_row(self):
        q = PlaybackQueue()
        q.replace([10,20,30,40])
        q.select(10,0)
        q.select(40,3)
        q.select(20,1)
        self.assertEqual(q.previous_target(shuffle=True), (40,3,1))
        previous = q.previous_target(shuffle=True)
        q.select(previous[0],previous[1],previous[2])
        self.assertEqual(q.next_target(shuffle=True), (20,1,2))

    def test_ctrl_order_represented_as_ordered_queue(self):
        q = PlaybackQueue()
        q.replace([4,1,7])
        self.assertEqual(q.items, [4,1,7])
        q.extend([5,8])
        self.assertEqual(q.items, [4,1,7,5,8])

    def test_clear_and_rebuild(self):
        q = PlaybackQueue()
        q.replace([1,2,3])
        q.select(2,1)
        q.clear()
        self.assertEqual(q.items,[])
        q.replace([1,2,3])
        self.assertEqual(q.next_target(),(1,0,None))

    def test_history_prune_preserves_cursor(self):
        q = PlaybackQueue()
        q.replace([1,2,3,4])
        for i in (1,2,3):
            q.select(i,i-1)
        back = q.previous_target(shuffle=True)
        q.select(*back[:2], history_cursor=back[2])
        self.assertEqual(q.history_cursor,1)
        q.prune({1,2,3,4})
        self.assertEqual(q.history_cursor,1)
        self.assertEqual(q.next_target(shuffle=True)[:1],(3,))

    def test_removing_queue_slot_adjusts_current_index(self):
        q=PlaybackQueue()
        q.replace([1,2,3])
        q.select(3,2)
        q.remove(0)
        self.assertEqual(q.current_index,1)
        self.assertEqual(q.items,[2,3])

if __name__ == '__main__': unittest.main()

class ShuffleCycleTests(unittest.TestCase):
    def test_shuffle_exhausts_queue_without_repeat(self):
        q=PlaybackQueue()
        q.replace([1,2,3])
        q.select(1,0)
        seen={1}
        for _ in range(2):
            nxt=q.next_target(shuffle=True)
            self.assertIsNotNone(nxt)
            self.assertNotIn(nxt[0],seen)
            seen.add(nxt[0])
            q.select(nxt[0],nxt[1])
        self.assertEqual(seen,{1,2,3})
        self.assertIsNone(q.next_target(shuffle=True,repeat=False))
        self.assertIsNotNone(q.next_target(shuffle=True,repeat=True))
