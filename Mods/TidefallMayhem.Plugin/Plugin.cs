using System;
using System.Collections.Generic;
using System.IO;
using Path = System.IO.Path;
using System.Reflection;
using BepInEx;
using BepInEx.Logging;
using HarmonyLib;
using Amplitude;
using Amplitude.Framework;
using Amplitude.Framework.Modifications;
using Amplitude.Framework.Simulation;

namespace TidefallMayhem
{
    [BepInPlugin("local.el2.tidefallmayhem", "Tidefall Mayhem", "0.5.0")]
    public sealed class Plugin : BaseUnityPlugin
    {
        internal static ManualLogSource Log;
        internal static string AssetRoot;
        internal static readonly HashSet<object> RegisteredManagers = new HashSet<object>();
        private Harmony harmony;
        private void Awake()
        {
            Log = Logger;
            AssetRoot = Path.Combine(Path.GetDirectoryName(Info.Location), "Assets");
            if (!File.Exists(Path.Combine(AssetRoot, "TidefallMayhem", "mod-info.json")))
            {
                Log.LogError("Missing Assets/TidefallMayhem/mod-info.json; plugin was not enabled.");
                return;
            }
            harmony = new Harmony("local.el2.tidefallmayhem");
            harmony.PatchAll(typeof(Plugin).Assembly);
            Log.LogInfo("Tidefall Mayhem 0.5.0 ready: automatic first-turn and Tidefall drafts; human players only; no mode-choice event.");
        }
        private void OnDestroy() { if (harmony != null) harmony.UnpatchSelf(); }

        internal static bool HandleGrant(BaseSimulationEntity empire, StaticString descriptor, int delta)
        {
            string name = descriptor.ToString();
            const string prefix = "TM_Grant_";
            if (!name.StartsWith(prefix, StringComparison.Ordinal)) return true;
            string code = name.Substring(prefix.Length);
            if (!Codes.Contains(code)) throw new InvalidOperationException("Unknown Mayhem augment " + code);
            int count = StackCounter.Read(bit => empire.ContainsDescriptor(new StaticString(BitName(code, bit))));
            int next = StackCounter.Update(count, delta, (bit, enabled) =>
            {
                StaticString bitDescriptor = new StaticString(BitName(code, bit));
                if (enabled) empire.AddDescriptor(bitDescriptor);
                else empire.RemoveDescriptor(bitDescriptor);
            });
            Log.LogInfo("Augment " + code + " -> " + next + " on empire entity " + empire.GetDebugName());
            return false;
        }
        internal static string BitName(string code, int bit) { return "TM_Stack_" + code + "_" + bit.ToString("00"); }
        internal static readonly HashSet<string> Codes = new HashSet<string>(AugmentCatalog.Codes, StringComparer.Ordinal);
    }

    [HarmonyPatch]
    internal static class RegisterAssets
    {
        static MethodBase TargetMethod()
        {
            return AccessTools.Method(typeof(ModificationManager), "Amplitude.Framework.Modifications.IModificationService.Initialize");
        }
        static void Postfix(ModificationManager __instance)
        {
            if (Plugin.RegisteredManagers.Contains(__instance)) return;
            var type = typeof(ModificationManager);
            var controller = new FileSystemModificationController(Plugin.AssetRoot);
            AccessTools.Method(type, "RegisterModificationController").Invoke(__instance, new object[] { "tidefallmayhem", controller });
            object[] create = { "tidefallmayhem", "TidefallMayhem", null };
            AccessTools.Method(type, "CreateModification").Invoke(__instance, create);
            if (create[2] == null) throw new InvalidOperationException("Tidefall Mayhem asset registration returned no modification.");
            AccessTools.Method(type, "RegisterModification").Invoke(__instance, new[] { create[2] });
            ModdingUtils.IsModdingEnabled = true;
            Plugin.RegisteredManagers.Add(__instance);
            Plugin.Log.LogInfo("Registered built-in augment assets without changing the user's mod configuration.");
        }
    }

    [HarmonyPatch(typeof(BaseSimulationEntity), "AddDescriptor", new Type[] { typeof(StaticString) })]
    internal static class GrantAugment
    {
        static bool Prefix(BaseSimulationEntity __instance, StaticString __0) { return Plugin.HandleGrant(__instance, __0, 1); }
    }
    [HarmonyPatch(typeof(BaseSimulationEntity), "RemoveDescriptor", new Type[] { typeof(StaticString) })]
    internal static class RevertAugment
    {
        static bool Prefix(BaseSimulationEntity __instance, StaticString __0) { return Plugin.HandleGrant(__instance, __0, -1); }
    }

    internal static class TieredOfferPools
    {
        internal static string Name(object definition)
        {
            return AccessTools.Property(definition.GetType(), "Name").GetValue(definition, null).ToString();
        }
        internal static void Prepare(object pool, string previous)
        {
            object category = AccessTools.Field(pool.GetType(), "NarrativeEventCategoryDefinition").GetValue(pool);
            string categoryName = Name(category);
            if (categoryName != "TM_Category_Start" && categoryName != "TM_Category_Tide") return;
            var byType = AccessTools.Field(pool.GetType(), "NarrativeEventDefinitions").GetValue(pool) as System.Collections.IDictionary;
            if (byType == null) return;
            foreach (System.Collections.DictionaryEntry entry in byType)
            {
                var list = entry.Value as System.Collections.IList;
                if (list != null) TieredDrafts.Reorder(list, Name, previous);
            }
        }
    }

    [HarmonyPatch]
    internal static class PrepareInitialTiers
    {
        static MethodBase TargetMethod()
        {
            return AccessTools.Method(AccessTools.TypeByName("Amplitude.Mercury.Simulation.NarrativeEventManager"), "CollectNarrativeEventDefinitions");
        }
        static void Postfix(object __0) { TieredOfferPools.Prepare(__0, null); }
    }

    [HarmonyPatch]
    internal static class ShuffleReusableOffers
    {
        static MethodBase TargetMethod()
        {
            return AccessTools.Method(AccessTools.TypeByName("Amplitude.Mercury.Simulation.NarrativeEventManager"), "TryTriggerEventDefinition");
        }
        static void Postfix(object __0, object __2, bool __result)
        {
            if (!__result) return;
            string selected = TieredOfferPools.Name(__0);
            if (!selected.StartsWith("TM_Start_", StringComparison.Ordinal) && !selected.StartsWith("TM_Tide_", StringComparison.Ordinal)) return;
            TieredOfferPools.Prepare(__2, selected);
        }
    }
}
