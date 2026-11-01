using System;
using System.Collections;
namespace TidefallMayhem
{
    internal static class TieredDrafts
    {
        internal static string Tier(string name)
        {
            if (name.IndexOf("_Prismatic_", StringComparison.Ordinal) >= 0) return "Prismatic";
            if (name.IndexOf("_Gold_", StringComparison.Ordinal) >= 0) return "Gold";
            return "Silver";
        }
        internal static string TierForRoll(uint roll)
        {
            roll %= 100;
            return roll < 40 ? "Silver" : roll < 80 ? "Gold" : "Prismatic";
        }
        private static uint Next(ref uint state)
        {
            if (state == 0) state = 0x6D2B79F5;
            state ^= state << 13; state ^= state >> 17; state ^= state << 5;
            return state;
        }
        internal static void Reorder(IList list, Func<object, string> name, string previous)
        {
            if (list.Count < 2) return;
            uint state = 2166136261;
            foreach (object item in list)
                foreach (char c in name(item)) state = unchecked((state ^ c) * 16777619);
            for (int i = list.Count - 1; i > 0; i--)
            {
                int j = (int)(Next(ref state) % (uint)(i + 1));
                object temp = list[i]; list[i] = list[j]; list[j] = temp;
            }
            string tier = TierForRoll(Next(ref state));
            for (int i = 0; i < list.Count; i++)
            {
                string candidate = name(list[i]);
                if (Tier(candidate) != tier || candidate == previous) continue;
                object temp = list[0]; list[0] = list[i]; list[i] = temp;
                return;
            }
        }
    }
}
