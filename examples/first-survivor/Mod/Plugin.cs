using BepInEx;
using R2API;
using R2API.Utils;
using RoR2;
using RoR2.ContentManagement;

namespace WorkbenchRecruit
{
    [BepInPlugin(Identity.Guid, Identity.Name, Identity.Version)]
    [BepInDependency("com.bepis.r2api.prefab")]
    [BepInDependency("com.bepis.r2api.language")]
    [NetworkCompatibility(CompatibilityLevel.EveryoneMustHaveMod, VersionStrictness.EveryoneNeedSameModVersion)]
    public sealed class Plugin : BaseUnityPlugin
    {
        private RecruitContent content;

        private void Awake()
        {
            LanguageAPI.Add("WORKBENCH_RECRUIT_NAME", Identity.Name);
            LanguageAPI.Add("WORKBENCH_RECRUIT_DESCRIPTION", "An asset-free learning survivor with Commando's native skills. Runtime acceptance is still required.");
            LanguageAPI.Add("WORKBENCH_RECRUIT_OUTRO", "...and so the first bounded experiment ended.");
            content = new RecruitContent(Logger);
            ContentManager.collectContentPackProviders += Collect;
        }

        private void Collect(ContentManager.AddContentPackProviderDelegate addProvider)
        {
            addProvider(content);
        }

        private void OnDestroy()
        {
            ContentManager.collectContentPackProviders -= Collect;
        }
    }
}
