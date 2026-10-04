using System;
using System.Collections;
using System.Linq;
using BepInEx.Logging;
using R2API;
using RoR2;
using RoR2.ContentManagement;
using UnityEngine;

namespace WorkbenchRecruit
{
    // Original minimal provider: keep native movement, input, camera and skills.
    internal sealed class RecruitContent : IContentPackProvider
    {
        private readonly ContentPack content = new ContentPack();
        private readonly ManualLogSource log;
        public string identifier => Identity.Guid;

        internal RecruitContent(ManualLogSource logSource) { log = logSource; }

        public IEnumerator LoadStaticContentAsync(LoadStaticContentAsyncArgs args)
        {
            try { Construct(); }
            catch (Exception error)
            {
                log.LogError("Workbench Recruit content construction failed: " + error);
                throw;
            }
            args.ReportProgress(1f);
            yield break;
        }

        private void Construct()
        {
            var stockBody = Load("Prefabs/CharacterBodies/CommandoBody");
            var stockDisplay = Load("Prefabs/CharacterDisplays/CommandoDisplay");
            var stockMaster = Load("Prefabs/CharacterMasters/CommandoMonsterMaster");
            // InstantiateClone registers network prefabs itself. Do not register twice.
            var body = PrefabAPI.InstantiateClone(stockBody, "WorkbenchRecruitBody", true);
            var master = PrefabAPI.InstantiateClone(stockMaster, "WorkbenchRecruitMonsterMaster", true);
            var display = PrefabAPI.InstantiateClone(stockDisplay, "WorkbenchRecruitDisplay", false);
            body.GetComponent<CharacterBody>().baseNameToken = "WORKBENCH_RECRUIT_NAME";
            master.GetComponent<CharacterMaster>().bodyPrefab = body;
            var survivor = ScriptableObject.CreateInstance<SurvivorDef>();
            survivor.cachedName = "WorkbenchRecruit";
            survivor.bodyPrefab = body;
            survivor.displayPrefab = display;
            survivor.displayNameToken = "WORKBENCH_RECRUIT_NAME";
            survivor.descriptionToken = "WORKBENCH_RECRUIT_DESCRIPTION";
            survivor.outroFlavorToken = "WORKBENCH_RECRUIT_OUTRO";
            survivor.mainEndingEscapeFailureFlavorToken = "WORKBENCH_RECRUIT_OUTRO";
            survivor.primaryColor = new Color(0.25f, 0.75f, 0.85f);
            survivor.desiredSortPosition = 110f;
            content.bodyPrefabs.Add(new[] { body });
            content.masterPrefabs.Add(new[] { master });
            content.survivorDefs.Add(new[] { survivor });
            log.LogInfo("Workbench Recruit native content constructed; stock skills retained.");
        }

        private static GameObject Load(string key)
        {
            var asset = LegacyResourcesAPI.Load<GameObject>(key);
            if (!asset) throw new InvalidOperationException("Required native prefab missing: " + key);
            return asset;
        }

        public IEnumerator GenerateContentPackAsync(GetContentPackAsyncArgs args)
        {
            // Public catalog collections; no private/publicized member dependency.
            args.output.bodyPrefabs.Add(content.bodyPrefabs.ToArray());
            args.output.masterPrefabs.Add(content.masterPrefabs.ToArray());
            args.output.survivorDefs.Add(content.survivorDefs.ToArray());
            args.ReportProgress(1f);
            yield break;
        }

        public IEnumerator FinalizeAsync(FinalizeAsyncArgs args)
        {
            args.ReportProgress(1f);
            yield break;
        }
    }
}
