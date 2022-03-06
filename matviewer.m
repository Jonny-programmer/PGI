num_frames = 128;
side = 16;

m = matfile('static/mat/2021-09-29-d1.mat');
frames = m.frames;
figure;
for i= 1:num_frames
    frame_view = reshape(frames(i,:,:), [side side]);
    imagesc(frame_view);
    colorbar;
    pause(0.1);
end
%frames1 = zeros(16);
%frames1(:,:) = frames(1,:,:);