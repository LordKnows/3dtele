# Deep read of base paper
Verified against the full arXiv v1 HTML, including appendices A.1 to A.8, which reproduce the supplementary document.

INPUTS
- N fixed, synchronized RGB cameras.
- Sec. 3 says poses are computed once with COLMAP. A.7 says "we use the provided camera parameters". The paper does not reconcile the two.
- Per-view depth D_n^t comes from RAFT-Stereo on "manually selected image pairs" for DyNeRF and Google Spaces, or from a sensor for ScanNet. RGB-D cameras are mentioned only as an option (ref. Holoportation).
- The paper never says how stereo pairs or depth are produced for the test sequences.
- Stereo depth time is NOT counted in the runtime.

VIEW SELECTION
- The K input cameras closest to the target view are used, excluding the held-out test camera itself.
- K=4 for DyNeRF and ENeRF-Outdoor; K=2 for D3DMV.
- All baselines use the same K views.
- Test views are held-out rig cameras: 9 for DyNeRF, 3 for ENeRF-Outdoor, 4 for D3DMV. So every quantitative novel view is an interpolated viewpoint on the rig itself; there is no extrapolation.

(1) FORWARD RENDERING
- Every pixel of each of the K views is unprojected with its depth to a fully opaque, isotropic 3D Gaussian. Its colour is the pixel colour and its scale is set analytically so it projects to one source pixel.
- Each view is rendered SEPARATELY with the original 3DGS rasteriser. This gives a warped RGB image, an accumulated alpha and a depth per view.
- They explicitly reject rendering all views in one pass (the GPS-Gaussian / GS-LRM style), citing flying pixels and z-fighting.
- They also reject network-predicted Gaussian parameters. Their stated reason: on dense pixel grids those predictions converge to near-constant values, and letting scale vary to fill disocclusions hurt PSNR.

(2) TEMPORALLY CONSISTENT DEPTH
- Soft difference mask per input view: M = min(|I_t − I_{t−1}|/0.7 + 0.6, 1). It is computed at quarter resolution, then 3x3 max-pooled and bilinearly upsampled.
- Recursive filter: D_dot^t = M·D^t + (1−M)·D_dot^{t−1}. Because M ≥ 0.6, at least 60% of the new depth is always taken. In static regions this is a mild EMA with factor ≤ 0.4.
- Image-based TSDF (after Lawrence et al., Project Starline):
  - Each ray sample p is projected into the K views; the signed distance is s_k = z_k − D_k[u,v].
  - Values are clamped to τ = 0.02 m, a metric unit.
  - Samples are fused with weight ω_k = min(0.001·(ν_k/49)^{-1/2}, 1), where ν_k is the truncated local depth variance in a 7x7 window. ω_k = 0 when s_k < −τ.
  - Ray marching steps by 0.8·s until the sign changes, then refines with 3 bisection steps.
  - Near/far bounds and ray start are not specified.
- The previous frame's rendered novel-view depth 𝒟^{t−1} is fused as an extra TSDF input with weight ω_tmp = min(β·ω_acc·max(1−𝓜^t, 0), η).
  - η = 15.
  - ω_acc = ω_tmp^{t−1} + Σ_k ω_k^{t−1}.
  - 𝓜^t is the channel-wise max of the K difference masks, forward-splatted into the target view.
  - This β is a different parameter from the 0.6 above and its value is not given.
  - The paper does not describe how 𝒟^{t−1} is reprojected when the target camera moves between frames.

(3) GEOMETRY-GUIDED BLENDING
- A 4-level U-Net takes (9K+1) channels:
  - 3K warped RGB
  - K depth maps (written {D_k^t} in A.4 but {𝒟_k^t} in Sec. 3.3, so it is ambiguous whether these are warped depths or source depths)
  - K alpha maps
  - 1 TSDF depth
  - K maps of dot(input ray, TSDF normal)
  - K maps of dot(input ray, target direction)
  - K maps of camera distance, spatially broadcast
  - K maps of dot(input direction, target direction)
- It outputs K per-pixel blend weights, a background weight w_BG AND a background image I_BG. So the network can synthesise pixels, but only through a small per-frame CNN.
- Output: I_FG = Σ_k I_k·α_k·w_k / (α_k·w_k). The denominator is printed without the sum, which is a typo. Final I = (1−w_BG)·I_FG + w_BG·I_BG.
- Loss: 0.8·L1 + 0.2·SSIM + 0.1·L_depth + 0.1·L_mask.
  - L_depth is the L1 between the TSDF depth and the depth composited with the same weights.
  - L_mask is the L1 between w_BG and a binary mask of empty regions.
- There is NO temporal loss.

TRAINING
- Adam, lr 2e-4, weight decay 1e-5, 150K iterations, batch 12, 640x352 crops, one V100.
- ScanNet: static. Inputs are frames within ±30 of the target, excluding ±4.
- 3 DyNeRF scenes and Google Spaces: input and target views are sampled at a SINGLE time instant.
- So the network never sees a video sequence in training; temporal behaviour comes only from the inputs.
- The DyNeRF training scenes share the same kitchen, rig and lighting as the two test scenes (Sear Steak, Flame Steak).
- Torch-TensorRT is used at inference. The TSDF is custom CUDA.

RUNTIME (Table 4, DyNeRF at 1352x1014; test GPU not stated)
- Splatting 10 ms, TSDF 6 ms, blending 23 ms with TensorRT or 65 ms without.
- That sums to about 39 ms with TensorRT, or about 81 ms without.
- The text says "≈100 ms even without TensorRT" and compares it with GPS-Gaussian's 143.4 ms.
- Stereo depth, difference masks and disk I/O are excluded.
- Runtime grows roughly linearly with K; quality saturates at K ≥ 4.

EVALUATION
- First 100 frames only.
- Resolutions: DyNeRF 1352x1014; ENeRF-Outdoor rendered at 960x540 but scored at 480x270 because of sync and colour-calibration errors; D3DMV 640x360 (compressed version).
- Metrics: PSNR, SSIM, LPIPS, L1; temporal TCC (an SSIM of frame-difference images, adapted), STED, SDT; view SDV (std of L1 error across views); EPI and x–t slices shown qualitatively.
- Baselines: IBRNet and ENeRF with the authors' pretrained weights. FWD and GPS-Gaussian retrained on the paper's data.
- 4DGS, 4K4D and MVSplat appear only in one qualitative figure (Fig. 12).
- Ablations appear to be DyNeRF only and single-run.

PUBLICATION
- CVPR 2025. The project page has no code link.

## assumptions
- Fixed, rigid, pre-calibrated rig: camera poses never change over time. This is what makes per-pixel temporal differencing of input images possible.
- Cameras are tightly synchronized and colour-calibrated. The paper admits that misalignment causes blur.
- Reasonably accurate per-view depth is available for every input view at every frame, from offline RAFT-Stereo on hand-picked stereo pairs or from a depth sensor. The time to produce it is excluded from the runtime budget.
- Mostly Lambertian scenes. Specular or non-Lambertian surfaces break the depth and therefore the TSDF guidance.
- Scene scale is metric, or at least consistent, because the TSDF truncation is a hard-coded 0.02 m.
- Target viewpoints lie near the capture rig, interpolating between the K nearest cameras. Test views are always held-out rig cameras.
- A change in pixel colour signals motion and no change signals a static region. This fails under illumination changes, flicker, auto-exposure, noise, flames, and moving surfaces that are uniformly coloured or textureless.
- Scenes are 'dynamic actors in diverse static environments'. All three test datasets fit this description, so the dynamic region is small relative to the background.
- Disocclusions are small enough for a small per-frame CNN's background image to plausibly fill them.
- Temporal consistency can be obtained purely by making the inputs (depth) consistent, without any temporal loss or recurrent state in the network.
- One target view is rendered at a time. There is no stereo pair, no multi-viewer setting and no network transmission.
## weaknesses stated
- Relies strongly on accurate geometry. It fails in specular regions where depth is bad. The blend net still gives reasonable single frames there, but they are not temporally or view consistent (Fig. 9, EPI discontinuities).
- Requires well-synchronized and calibrated cameras. Calibration errors blur the result, and ENeRF-Outdoor needed half-resolution scoring because of sync and colour-calibration errors.
- Only the K nearest views are fused into the TSDF. When the viewpoint moves and the K-set changes, the TSDF depth can still change slightly. More K helps but costs time, and runtime is roughly linear in K.
- Global geometry trades off local appearance flexibility. The introduction concedes this about global-geometry methods, and they only claim to mitigate it through image-based rendering.
- Pixel-sized Gaussians plus separate per-view rendering still leave holes and flying pixels from disocclusion and depth errors. These must be fixed by the blend network.
## weaknesses unstated
- (Verified) The 'online / interactive' claim leaves out depth estimation. RAFT-Stereo on 'manually selected image pairs' for up to 22 cameras at 1352x1014 is excluded from Table 4. The stereo pairs are manually curated, which cannot run live, and the test-time depth protocol is not described. For a real 3D-telepresence system, depth is often the dominant cost.
- (Verified, contradicts the task premise) The runtime numbers do not add up and 100 ms is not real time. Table 4 sums to about 39 ms with TensorRT or about 81 ms without, yet the text says '≈100 ms even without TensorRT'. The test GPU is unspecified; V100 is only mentioned for training. The GPS-Gaussian comparison references the wrong figure. Even the best case (about 25 fps, one mono view) is far from the 72–90 Hz × 2 eyes an HMD needs, and motion-to-photon latency is never measured.
- (Verified) The claim of 'marked improvement' on ENeRF-Outdoor is contradicted by the paper's own Table 2. There, Ours scores PSNR 24.01 vs ENeRF 25.79, SSIM 0.703 vs 0.722 and L1 12.02 vs 9.84; only LPIPS is better. In Table 1 it is also worse than ENeRF on STED (44.49 vs 32.31) and SDT (0.193 vs 0.189). The method loses on the only truly out-of-domain outdoor dataset.
- (Verified) There is likely train/test domain leakage on DyNeRF. Training uses 3 DyNeRF scenes, testing uses Sear Steak and Flame Steak, and all DyNeRF scenes share the same kitchen, rig, lighting and background. Meanwhile IBRNet and ENeRF use off-the-shelf pretrained weights and only FWD and GPS-Gaussian are retrained. The headline DyNeRF gain (31.17 vs 29.51) is therefore confounded by in-domain training.
- (Verified) The headline contribution, TSDF guidance, adds nothing measurable to fidelity. The ablation gives PSNR 31.16 → 31.17, LPIPS 0.197 → 0.191 and TCC 0.869 → 0.872. Only STED moves noticeably (95.4 → 68.8). Temporal filtering alone likewise leaves PSNR unchanged. The ablations are a single run on DyNeRF with no error bars. Almost all of the gain over the distance-blending baseline (26.08 → 31.16) comes from having a learned blend net at all.
- (Verified) There is no temporal loss and no temporal training data. The blend net is trained on single time instants, and ScanNet is static. Temporal stability depends entirely on the inputs, so any flicker the CNN itself introduces (for example in I_BG) is uncontrolled. The TCC gains are small (0.872 vs 0.867).
- (Verified, partially corrects the task premise) The net does predict a background image I_BG, so it CAN hallucinate disocclusions. But this comes from a 4-level U-Net with no multi-frame memory and no generative prior, trained with a crude mask loss. Large disocclusions, for example around a person seen from a viewpoint far off the rig, are not evaluated. Pixels that were visible in earlier frames but are occluded now (long-term memory) are never used, even though the rig is static and the background persists.
- (Verified) The temporal filter is weak and heuristic. Because the mask floor β = 0.6, static regions get at most 40% of the previous depth each frame, which is short memory. The thresholds are hand-set on raw RGB differences. They will misclassify illumination changes, shadows, flames (Flame Steak itself contains fire), auto-exposure and sensor noise as motion. Textureless or uniformly coloured moving objects will be treated as static, giving stale-depth ghosting. The η = 15 cap and the unspecified second β are further hand-tuned constants.
- (Verified, not addressed) Reusing the previous-frame depth assumes the target camera is fixed. 𝒟^{t−1} is fused in target-image space, and there is no description of how it is warped when the viewpoint changes between frames. Temporal metrics are computed only at fixed held-out cameras and view metrics only at fixed time, so the realistic telepresence case (head moving while the scene moves) is never evaluated.
- (Verified) The 'global' geometry is local. Only the K nearest views are fused, so view consistency holds only while the K-set is constant. There is no hysteresis or soft weighting over all N cameras, so popping when views switch is only mitigated through depth; the RGB blend can still switch abruptly.
- The TSDF has a hard metric truncation of 0.02 m and a fixed 0.001 confidence constant. Stereo depth error grows roughly quadratically with distance, so a fixed τ is too tight for far backgrounds (outdoor scenes) and too loose for fine detail. Ray-march near/far bounds and scene bounding are unspecified, and the dependence on metric scale conflicts with COLMAP poses, whose scale is arbitrary.
- Fully opaque, isotropic, pixel-sized Gaussians cannot model semi-transparency, hair, motion blur, thin structures or view-dependent effects. The analytic scale ignores surface slant, so grazing-angle surfaces stretch or leave gaps. Their argument that learned parameters 'converge to constants' is anecdotal and has no ablation table.
- View-dependent appearance comes only from re-weighting the K observed colours. There is no reflectance model, so specularity will be baked in or blended as ghosts even where depth is fine.
- There is no bandwidth, compression or network-streaming analysis. Every renderer needs K full-resolution RGB and depth streams from a static rig. This is central to telepresence but is ignored, and it is unclear whether rendering happens at the sender or the receiver.
- Per-viewer cost: each novel view requires its own splat, TSDF and CNN pass. Stereo (two eyes) doubles the cost and several remote viewers multiply it linearly. Binocular consistency between the two eyes is not studied.
- Training data is tiny and narrow: ScanNet (static, sensor depth), 3 DyNeRF scenes and Google Spaces. There are no humans at scale and no outdoor dynamic training data, which limits generalisation. The poor ENeRF-Outdoor result is consistent with this.
- The paper does not handle partial depth failures in a principled way. Depth confidence is only a local-variance heuristic, and the network gets no per-pixel uncertainty from the stereo model.
- Reproducibility: no code or weights have been released. The project page has no code link as of 2026-09-24. The stereo pairs were hand-curated and several hyperparameters are unspecified.
## eval gaps
- Only the first 100 frames (about 3.3 s at 30 fps) per sequence. Long-horizon drift and error accumulation from the recursive depth filter and previous-frame TSDF feedback are never tested.
- Only 2 DyNeRF test scenes, and they are in-domain because training used other DyNeRF scenes from the same kitchen. ENeRF-Outdoor has only 3 test views and D3DMV only 4, on its compressed 640x360 version.
- ENeRF-Outdoor is scored at 480x270 (downsampled) because of sync problems, which hides high-frequency failures. Even so, the method loses to ENeRF on PSNR, SSIM and L1.
- No moving-camera-plus-dynamic-scene evaluation. Temporal metrics are at fixed held-out cameras and view metrics (EPI, SDV) at a fixed time. No free trajectories, no extrapolation beyond the rig, no head-tracked VR paths.
- No ground truth at truly novel off-rig viewpoints. All test views are real rig cameras between neighbours, so disocclusion difficulty is low.
- The temporal metrics are non-standard or weak. TCC is 'adapted' to colour, SDV measures the spread of error across views rather than consistency, and there is no warping-error metric based on optical flow (for example the one from Lai et al. 2018) and no perceptual flicker metric such as a VMAF-style measure.
- No user study or perceptual evaluation. There is no HMD, no stereoscopic viewing and no latency measurement, despite the Meta Reality Labs VR motivation.
- Unfair or incomplete baselines: ENeRF and IBRNet use pretrained weights while FWD and GPS-Gaussian are retrained. There is no quantitative comparison with the image-based TSDF of Project Starline (Lawrence et al.), with the depth-based free-viewpoint system of Guo et al. (TMM), with streaming 4DGS methods (3DGStream, IGS CVPR 2025), or with a post-hoc video deflickering or temporal-consistency baseline applied to ENeRF or GPS-Gaussian outputs. 4DGS, 4K4D and MVSplat appear only in a single qualitative figure.
- The runtime breakdown excludes depth estimation, the difference masks and I/O, and does not state the GPU. There is no end-to-end system latency, no fps at different resolutions or values of K, and no memory numbers.
- No robustness sweeps over depth noise, depth source (sensor vs stereo vs monocular foundation-model depth), calibration or sync error, illumination change, or number of rig cameras.
- Ablations are DyNeRF-only and single-seed, with no confidence intervals. No ablation of the hyperparameters (λ_t, β, η, τ, w). No ablation on the depth input to the blend net, or of the camera-feature channels.
- No bandwidth, compression or streaming evaluation, and no multi-viewer or stereo scaling test.
## followups
- Geometry-guided Online 3D Video Synthesis with Multi-View Temporal Consistency (CVPR 2025 open-access version) https://openaccess.thecvf.com/content/CVPR2025/papers/Ha_Geometry-guided_Online_3D_Video_Synthesis_with_Multi-View_Temporal_Consistency_CVPR_2025_paper.pdf — Published version of this paper (CVPR 2025, DOI 10.1109/CVPR52734.2025.01053). arXiv has only v1 (25 May 2025). CVF hosts a 74 MB supplementary zip; the arXiv appendix A.1–A.8 contains the supplementary text. Project page: https://nkhan2.github.io/projects/geometry-guided-2025 (no code link). Talk: https://www.youtube.com/watch?v=lusFyhJ52BQ
- REON-NVS: Real-Time Online Novel-View Synthesis from Sparse-View Videos (Kim, Kim, Kwon, Shin, Cho; POSTECH), ECCV 2026 https://doi.org/10.1007/978-3-032-37321-2_18 — The only on-topic paper that CITES this work (found via OpenAlex's cites: filter). It is a direct competitor or follow-up in real-time online NVS from sparse multi-view video. I found no arXiv version; the ECCV 2026 acceptance is listed at https://cg.postech.ac.kr/2026/06/19/5-papers-will-be-presented-at-eccv-2026/
- Accelerating Surgical Skill Acquisition by Using Multi-View Bullet-Time Video Generation (Applied Sciences 2025) https://doi.org/10.3390/app15168830 — Cites this paper (OpenAlex). It is an application-side citation using multi-view video synthesis, not a method follow-up. Overall citation count is low: OpenAlex 3, Semantic Scholar 1 as of 2026-09.
- LiveStre4m: Feed-Forward Live Streaming of Novel Views from Unposed Multi-View Video (arXiv 2604.06740, Apr 2026) https://arxiv.org/abs/2604.06740 — Concurrent or later competitor, not a citer. Uses a multi-view ViT on keyframes plus a diffusion-transformer temporal interpolation and super-resolution module, works on unposed rigs, about 0.07 s per frame at 1024x768 on an H100. Evaluated on Neural3DVideo (the DyNeRF dataset) and MeetRoom against 3DGStream, IGS and others. It does not cite Ha et al.
- Online Neural Space Time Memory for Dynamic Novel View Synthesis (Google/UW, arXiv 2607.15271, Jul 2026) https://arxiv.org/abs/2607.15271 — Adds the long-term memory this paper lacks: periodic memorisation plus per-frame application with cross-view attention, about 28 ms per frame at 256x256 on an H100, trained on MVHumanNet++. It does not cite Ha et al. It directly addresses the missing reuse of pixels that were visible in earlier frames but are occluded now.
- Tele360: Real-Time Feed-Forward Human Reconstruction from Sparse Unposed Cameras (Tsinghua, arXiv 2609.15032, Sep 2026) https://arxiv.org/html/2609.15032 — Telepresence-oriented, 4–6 uncalibrated 2K cameras, more than 25 FPS on an RTX 5090, with differentiable Levenberg–Marquardt camera refinement. It targets this paper's calibration and sync limitation, but for humans only.
- Generalizable 3D Gaussian Splatting enabled Semantic Coding for Real-Time Immersive Video Communications (GS-SCNet, arXiv 2604.25330) https://arxiv.org/html/2604.25330v1 — Joint multi-view coding and feed-forward 3DGS, about 75% BD-rate saving over MV-HEVC+GPS-Gaussian at 19.2 FPS. It covers the bandwidth dimension this paper ignores.
- Instant Gaussian Stream: Fast and Generalizable Streaming of Dynamic Scene Reconstruction via Gaussian Splatting (CVPR 2025 Highlight) https://arxiv.org/abs/2503.16979 — A generalizable streaming 4D Gaussian baseline with anchor-driven motion and keyframe refinement. It is missing from this paper's comparison. Code: https://github.com/yjb6/IGS
- Stereo Any Video: Temporally Consistent Stereo Matching (ICCV 2025) https://arxiv.org/abs/2503.05549 — A temporally consistent video stereo model. It could replace this paper's per-frame RAFT-Stereo plus heuristic difference-mask filtering at the source.
- PPMStereo: Pick-and-Play Memory Construction for Consistent Dynamic Stereo Matching (arXiv 2510.20178) https://arxiv.org/abs/2510.20178 — Memory-based, temporally consistent dynamic stereo. Another candidate front-end for this pipeline's depth.
- RealCam: Real-Time Novel-View Video Generation with Interactive Camera Control (arXiv 2605.06051, May 2026) https://arxiv.org/abs/2605.06051 — A few-step autoregressive video diffusion model for real-time camera-controlled video-to-video. It shows that a generative, causal disocclusion filler is becoming feasible in real time, in contrast to this paper's small per-frame U-Net for the background image.
- Novel View Synthesis as Video Completion (arXiv 2604.08500) https://arxiv.org/abs/2604.08500 — Treats novel-view synthesis as video completion with a video diffusion prior. Relevant for replacing the blend and inpaint step with a generative prior.
- StreamSplat: Streaming Feed-Forward 3D Gaussian Splatting (arXiv 2608.01659) https://arxiv.org/html/2608.01659 — Found in search results only, not read in detail. Described there as streaming feed-forward Gaussian reconstruction with persistent Gaussian propagation and adaptive fusion, a possible stateful alternative to per-frame warp-and-blend.
- D-FCGS: Feedforward Compression of Dynamic Gaussian Splatting for Free-Viewpoint Videos (arXiv 2507.05859) https://arxiv.org/abs/2507.05859 — Feed-forward compression of dynamic Gaussian splatting for free-viewpoint video. Relevant to the streaming and bandwidth gap in this paper.
## status
Published at CVPR 2025. The arXiv comment reads "Accepted by CVPR 2025"; CVF open access and IEEE Xplore list DOI 10.1109/CVPR52734.2025.01053, and there is a CVPR poster page (https://cvpr.thecvf.com/virtual/2025/poster/34890).

Versions and materials:
- arXiv has ONLY v1 (submitted 25 May 2025); there is no v2 or v3.
- CVF hosts a supplementary zip (about 74 MB, likely videos). The supplementary text is included as appendix A.1–A.8 in the arXiv HTML.
- Project page: https://nkhan2.github.io/projects/geometry-guided-2025/ (paper and bibtex only). There is a YouTube presentation.
- No code, pretrained weights or data release is linked anywhere, as of 2026-09-24.

Citations are low: OpenAlex counts 3 and Semantic Scholar 1. The only on-topic citer I found is REON-NVS (ECCV 2026, POSTECH). The other citers are a 2025 Applied Sciences surgical bullet-time video paper and an unrelated 2026 ISCAIT pose-transfer paper. The most relevant 2026 successors in online multi-view novel-view synthesis do not cite it: LiveStre4m, Online Neural Space Time Memory, Tele360 and GS-SCNet.
