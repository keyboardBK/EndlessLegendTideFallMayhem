using System;
namespace TidefallMayhem
{
    internal static class StackCounter
    {
        internal const int BitCount = 16;
        internal static int Read(Func<int, bool> contains)
        {
            int count = 0;
            for (int bit = 0; bit < BitCount; bit++) if (contains(bit)) count |= 1 << bit;
            return count;
        }
        internal static int Update(int count, int delta, Action<int, bool> change)
        {
            int next = checked(count + delta);
            if (next < 0 || next > ushort.MaxValue) throw new ArgumentOutOfRangeException("delta", "Augment stack counter exceeds the native 16-bit range.");
            for (int bit = 0; bit < BitCount; bit++)
            {
                int flag = 1 << bit;
                if ((count & flag) != (next & flag)) change(bit, (next & flag) != 0);
            }
            return next;
        }
    }
}
