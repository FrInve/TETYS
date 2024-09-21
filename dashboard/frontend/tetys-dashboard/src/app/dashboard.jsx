"use client";
import React, { useState } from 'react';
import { Bar, Line } from 'react-chartjs-2';
import WordCloud from 'react-wordcloud';
import {
  AppBar,
  Toolbar,
  Typography,
  TextField,
  Box,
  Grid,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Slider,
  Paper,
  Checkbox
} from '@mui/material';
import Chart from 'chart.js/auto';


const fakeData = {
  wordClouds: [
    [{ text: 'variant', value: 100 }, { text: 'mutations', value: 90 }],
    [{ text: 'dystrophy', value: 80 }, { text: 'autosomal', value: 70 }],
    [{ text: 'spocdelta', value: 85 }, { text: 'infectivity', value: 65 }],
    [{ text: 'rvsv-sars2', value: 75 }, { text: 'epitopes', value: 55 }],
  ],
  chartData: {
    labels: ['2020-01', '2020-02', '2020-03', '2020-04', '2021-01', '2021-02', '2021-03', '2021-04'],
    datasets: [
      {
        label: 'Topic 124',
        data: [0.2, 0.3, 0.1, 0.4, 0.5, 0.6, 0.2, 0.3],
        borderColor: 'rgba(255, 99, 132, 1)',
        fill: false
      },
      {
        label: 'Topic 107',
        data: [0.1, 0.4, 0.2, 0.5, 0.3, 0.4, 0.5, 0.6],
        borderColor: 'rgba(54, 162, 235, 1)',
        fill: false
      },
      // Add more datasets for other topics here
    ]  
  },
  bsoluteFrequencies: [10, 20, 15, 30, 25, 35, 40, 50]
};
  
const Dashboard = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('124');
  const [timeRange1, setTimeRange1] = useState([0, 3]);
  const [timeRange2, setTimeRange2] = useState([4, 7]);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value)
  };

  const handleTopicChange = (event) => {
    setSelectedTopic(event.target.value)
  };

  const handleTimeRange1Change = (event, newValue) => {
    setTimeRange1(newValue)
  };

  const handleTimeRange2Change = (event, newValue) => {
    setTimeRange2(newValue)
  };

  return (
    <div>
        <AppBar position="static">
            <Toolbar>
            <Typography variant="h6">CORTOViz - The CORD-19 Topics Visualizer</Typography>
            </Toolbar>
        </AppBar>

        <Box p={3}>
            <TextField
            fullWidth
            label="Search a topic"
            variant="outlined"
            value={searchTerm}
            onChange={handleSearchChange}
            />
        </Box>

        <Grid container spacing={2} p={3}>
            <Grid item xs={12} md={3}>
                <Paper elevation={3}>
                    <Box p={2}>
                        {fakeData.wordClouds.map((words, index) => (
                            <div key={index}>
                                <Typography variant="subtitle2">Topic ID: {124 + index}</Typography>
                                <WordCloud words={words} options={{ fontSizes: [10, 60] }} />
                            </div>
                        ))}
                    </Box>
                </Paper>
            </Grid>
            <Grid item xs={12} md={9}>
                <Paper elevation={3}>
                    <Box p={2}>
                        <Line
                            data={{
                                labels: fakeData.chartData.labels,
                                datasets: fakeData.chartData.datasets
                            }}
                            options={{
                                scales: {
                                    x: { title: { display: true, text: 'Date' } },
                                    y: { title: { display: true, text: 'Relative Frequency (%)' } }
                                },
                                plugins: {
                                    annotation: {
                                        annotations: fakeData.chartData.labels.map((label, index) => ({
                                            type: 'line',
                                            xMin: index,
                                            xMax: index,
                                            borderColor: 'red',
                                            borderWidth: 1,
                                            label: {
                                                content: label,
                                                enabled: true,
                                                position: 'top'
                                            }
                                        }))
                                    }
                                }
                            }}
                        />
                        <Bar
                            data={{
                                labels: fakeData.chartData.labels,
                                datasets: [
                                    {
                                        label: 'Absolute Frequency',
                                        data: fakeData.absoluteFrequencies,
                                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                        borderColor: 'rgba(75, 192, 192, 1)',
                                        borderWidth: 1
                                    }
                                ]
                            }}
                            options={{
                                scales: {
                                    x: { title: { display: true, text: 'Date' } },
                                    y: { title: { display: true, text: 'Count' } }
                                }
                            }}
                        />
                    </Box>
                </Paper>
            </Grid>
        </Grid>

        <Box p={3}>
            <Paper elevation={3}>
                <Box p={2}>
                    <FormControl component="fieldset">
                        <FormLabel component="legend">Verify your hypothesis</FormLabel>
                        <RadioGroup row value={selectedTopic} onChange={handleTopicChange}>
                            <FormControlLabel value="124" control={<Radio />} label="124" />
                            <FormControlLabel value="107" control={<Radio />} label="107" />
                            <FormControlLabel value="262" control={<Radio />} label="262" />
                            <FormControlLabel value="86" control={<Radio />} label="86" />
                            <FormControlLabel value="165" control={<Radio />} label="165" />
                            <FormControlLabel value="295" control={<Radio />} label="295" />
                        </RadioGroup>
                    </FormControl>
                    <Box mt={2}>
                        <Typography>Time Range 1</Typography>
                        <Slider
                            value={timeRange1}
                            onChange={handleTimeRange1Change}
                            valueLabelDisplay="auto"
                            step={1}
                            marks
                            min={0}
                            max={7}
                        />
                        <Typography>Time Range 2</Typography>
                        <Slider
                            value={timeRange2}
                            onChange={handleTimeRange2Change}
                            valueLabelDisplay="auto"
                            step={1}
                            marks
                            min={0}
                            max={7}
                        />
                    </Box>
                    <Box mt={2}>
                        <Typography>
                            The observations of Topic {selectedTopic} in the chosen intervals are statistically
                            different (p-value: 0.00011, H-statistic: 15.03906)
                        </Typography>
                    </Box>
                </Box>
            </Paper>
        </Box>
    </div>
  );
};
  
export default Dashboard;