import * as React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid';

const videoSampleObject = {
  videos: [
    {
      title: 'MOCHAKK @ Club Space Miami -SUNRISE DJ SET presented by Link Miami Rebels',
      viewCount: 1443282,
      url: 'https://www.youtube.com/watch?v=4iKfR3UBDpQ',
    },
    {
      title: 'CARL COX @ Club Space Miami -SUNRISE DJ SET presented by Link Miami Rebels',
      viewCount: 1146755,
      url: 'https://www.youtube.com/watch?v=CTvkbzE4Jus',
    },
  ],
};

const Video = () => {
  return (
    <Box sx={{ p: 3, background: '#706677', minHeight: '100vh', mt: 4, borderRadius: 2 }}>
      <Typography
        variant="h5"
        gutterBottom
        sx={{ textAlign: 'center', mb: 4, fontSize: '1.5rem', color: "white" }}
      >
        Video Library
      </Typography>
      {videoSampleObject.videos.map((video, index) => {
        const videoId = video.url.split('v=')[1];

        return (
          <React.Fragment key={videoId}>
            <Card
              sx={{
                mb: 3,
                boxShadow: 1,
                borderRadius: 2,
                backgroundColor: '#fdfdfd',
                padding: 1,
              }}
            >
              <Grid container spacing={2} alignItems="center">
                {/* Left: Video iframe */}
                <Grid item xs={4}>
                  <CardMedia
                    component="iframe"
                    height="140"
                    src={`https://www.youtube.com/embed/${videoId}?autoplay=0`}
                    title={video.title}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    sx={{ borderRadius: 1 }}
                  />
                </Grid>
                {/* Right: Title and View Count */}
                <Grid item xs={8}>
                  <CardContent sx={{ padding: '8px' }}>
                    <Typography
                      variant="subtitle1"
                      gutterBottom
                      sx={{ fontSize: '0.9rem', fontWeight: 500, textAlign: 'left' }}
                    >
                      {video.title}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{ fontSize: '0.8rem', color: 'text.secondary', textAlign: 'left' }}
                    >
                      Views: {video.viewCount.toLocaleString()}
                    </Typography>
                  </CardContent>
                </Grid>
              </Grid>
            </Card>
            {index < videoSampleObject.videos.length - 1 && <Divider />}
          </React.Fragment>
        );
      })}
    </Box>
  );
};

export default Video;
