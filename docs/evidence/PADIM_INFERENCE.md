# Kalibra Governed PaDiM Inference Evidence v1.0

**Date:** 2026-07-05
**Scope:** C-5 Governed PaDiM inference only

## Governed Dataset Identity

- Dataset: VisA governed proxy acquisition `visa-acq-v1`
- Archive SHA-256: `2eb8690c803ab37de0324772964100169ec8ba1fa3f7e94291c9ca673f40f362`
- Files manifest SHA-256: `a01e02b043349d78b9dc958b12779fb48ccc30c0609719c739801a8dc503246c`
- Train split SHA-256 verified for identity: `9fa6abf23a487075bbe8f81becbfce471bbfc94e6e4ebc3f2cdf74db0abac736`
- Validation split SHA-256 consumed for inference: `79e6e3bf99589146143927e1e7861bb2f2b9c4b2502f4da8d8ecc3a274769cc5`
- Test split SHA-256 consumed for inference: `2d86ae7fa4cffe7f5f4aeb89f2c9c23351f44413da5d8aa0d5a3628a1c505510`
- Provenance SHA-256: `01933f8b335a520c5a22a0f9f38eb8544429343d580d3646855eae575de639d0`

## Governed PaDiM Artifact Identity

- Training label: `visa-padim-baseline-fit-v1`
- Training record SHA-256: `7d6171f3f05c30c4891969fa40451d0e960b4e5b8ac00b3d0e1d22f2ee9b8048`
- Training artifact hashes SHA-256: `00c625060c6e50fe7ab1da76125e3891d8be7e52838c846eaba52813461eeb32`
- Training metadata SHA-256: `c0178d823d0c440102c768f75799340586bd4c428bfa309862e8fb658b0ffad9`
- Training replay SHA-256: `dc5f66ee17533518489c893358cb30b8dd622277b5f38e21c0a0dd6e67fdd55f`
- Mu artifact SHA-256: `51568c211c324b9178837f0d862c01a9601dc3d3daa474c959bb32ef5758446b`
- Covariance inverse artifact SHA-256: `893af9e08d3543b5bd973ab913c1f2e8ed57d26a1bbb225b194d525cfc8df7b3`
- Feature indices artifact SHA-256: `1ca5583a7b498b4849e42717f24ebcf82d82a6c545b852814ada12b5c287cbe3`

## Deterministic Feature Extraction

- Backbone identity: `kalibra-fixed-patch-feature-backbone-v1`
- Backbone layer: `fixed_patch_statistics_64x64_patch8`
- Preprocessing contract id: `kalibra-padim-rgb64-bilinear-float64-patch8-v1`
- Feature indices: `[0, 2, 5, 6, 7, 9, 12, 13]`
- Dtype: `float64`
- Batch size: `16`

## Inference Surface

- Consumed splits: `['validation', 'test']`
- Inference image count: `6492`
- Split counts: `{'test': 4328, 'validation': 2164}`
- Aggregation policy: `maximum finite Mahalanobis distance over anomaly map`
- Aggregation identifier: `padim_anomaly_map_max_v1`
- Localization policy: `bounding box covering pixels equal to maximum anomaly-map value`
- Localization identifier: `padim_raw_anomaly_map_argmax_region_v1`
- Prediction surface: `InspectionPrediction`
- Raw measure field: `predicted_raw_anomaly_measure`
- Raw measure kind: `raw_anomaly_measure`
- Raw measure scale: `model_raw_anomaly_measure`

## Replay Verification

- Complete second inference run executed: `true`
- Identical feature tensors: `true`
- Identical anomaly maps: `true`
- Identical raw anomaly measures: `true`
- Identical localization: `true`
- Identical InspectionPrediction records: `true`
- Identical hashes: `true`
- Replay record: `data/visa/derived/padim/inference/replay/replay_verification.json`
- Replay record SHA-256: `e6e59b0e72750992d97fd39788a7a8a3b9f40a52a7783becdfa4f30dd779936c`

## Governed Inference Records

- Inference artifact hashes SHA-256: `c39dc13d4eccff0846253528d2fa3af4bb12349ca80fb9b90e631ef1fbdeb9bf`
- Metadata artifact hashes: `{'metadata/artifact_identity.json': '70ab2f957b5c11b2255c59f54310fc03701e11079f9af0af78ad5b989892495c', 'metadata/backbone_metadata.json': '55780631c506a03f3a6c9605caf52aa64d693f675a4ab5a4d3aed9b99d8b79ca', 'metadata/dataset_identity.json': 'a1c50e5b01333d48336000410a32e501e0120da576889765ba4f1e1ca0f9adb7', 'metadata/feature_indices.json': '064956f5ff6b70fe5e43525825dbf0b3d99d49a6b178cd1b499997e4af298dfe', 'metadata/inference_inputs.json': '17a043f02bae0209566a83721222ff22d61f72d639d9c677f001ec6720f5b1ca', 'metadata/inference_metadata.json': '78e8408534863096315a07f21da33265f970e44f369a9fa3e35743f2adea372f', 'metadata/numerical_config.json': '2a4963bf94458e861e3a535ea6a50efc5818cff8b4ba15577a0b05179abf90cb', 'metadata/preprocessing_contract.json': 'b239f587b442e1a64f9ee3f9615b0a912b897f860864c6a58568cb24573794e7'}`
- Local output artifact hashes: `{'anomaly_maps/test_anomaly_maps.npy': '21a959c9891815ea73ee7e23a47a1b4c15be18047ad58e2b721a7c24cdc15a9d', 'anomaly_maps/validation_anomaly_maps.npy': 'bdea53e85561e830ab1b45430f0df16e6769e9092124217fe5827ee30ac3d97d', 'predictions/test_predictions.jsonl': '35e2a8426a8e1bb59f8327f657eff79892dbbbad825acf19debee2a6436f8436', 'predictions/validation_predictions.jsonl': 'ebef96fad1a665e9e2cd4c2e9855f93f238b8a71a41971c56efbabd3ba5314c4'}`
- First five per-input inference hashes: `[{'input_id': 'visa-inference-input-4016f830f89425cd0ac90494', 'filename': 'candle/Data/Images/Anomaly/000.JPG', 'anomaly_map_sha256': 'a584b49ba08126cc840b3a90227a80776d8187fe45b6e083b5bfad65d4d195b5', 'prediction_sha256': '266b0c285a6f251b2758564cef8552f2687da84c9101e819fcd1be92d8c7289a'}, {'input_id': 'visa-inference-input-59515bd4788b2f555ab733fc', 'filename': 'candle/Data/Images/Anomaly/001.JPG', 'anomaly_map_sha256': '2b9b0235d0ad7b4f4c7294a1b19fa71836231c353ec77bf4f04aad3f447a1c41', 'prediction_sha256': '91170825e43a93fe3fae5d5ebdae1f4641919d20a9f9d4de73470107df2ca8c1'}, {'input_id': 'visa-inference-input-731528b6ae0713da079d72ab', 'filename': 'candle/Data/Images/Anomaly/002.JPG', 'anomaly_map_sha256': 'eda4d9b4f5fe4cfe182cc33ce925ec6d7515fc9c7c8aee28e6553cb57cacf495', 'prediction_sha256': '8e998adf20990ce713e281eb91aead2077490108f54ef7baba2825d33844be4b'}, {'input_id': 'visa-inference-input-adced0090eff32e4bb451c7e', 'filename': 'candle/Data/Images/Anomaly/003.JPG', 'anomaly_map_sha256': '513a3618842b7947fadbe280f4519d464cf094e511d7cac7ebb1cfb42584de39', 'prediction_sha256': '19396ab537c81e2dc656ad44d0dd520c52ee4148625ad65fa029e607750ba5ca'}, {'input_id': 'visa-inference-input-c660e3e92e2f9482f6fba0ce', 'filename': 'candle/Data/Images/Anomaly/008.JPG', 'anomaly_map_sha256': 'aed3294144b5b7a5de769106d1d58c03977122d981438770d33f8d442d1bb23d', 'prediction_sha256': 'c44b58069870e5016d6ce8fe8d26b0098a27bacd17f6e4d03c153d1fb09150e6'}]`

## Explicit Non-Claims

- No evaluation was executed.
- No Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, F1, metric, or benchmark was generated.
- No threshold or operating point was derived.
- No thresholded OK/defect classification was derived; the existing `InspectionPrediction` contract requires `predicted_judgement` when raw localization is present, so C-5 records `contract_required_defect_for_raw_localization_no_threshold_v1` only as a contract policy, not as a scientific or product classification.
- No calibration was performed.
- No ONNX export was produced.
- No fitting, retraining, artifact mutation, or preprocessing change was performed.
- No Trust, Review, Evidence Engine, Evaluation Engine, runtime, integration, prototype UI, provider interface, output mapping, or architecture code was modified.
- The raw anomaly measure is not a probability, not confidence, and not trust.
- This inference record makes no scientific claim and does not state that Kalibra detects defects.
