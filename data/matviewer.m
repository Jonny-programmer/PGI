num_frames = 128;
side = 16;

m = matfile('~/Downloads/data/frm_cc_00005115.mat');
frames = m.frames;
figure;
for i=1:num_frames
    frame_view = reshape(frames(i,:,:), [side side]);
    imagesc(frame_view);
    colorbar;
    pause(0.1);
end
%frames1 = zeros(16);
%frames1(:,:) = frames(1,:,:);