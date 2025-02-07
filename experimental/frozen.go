package frozen

import (
	"flag"
	"fmt"
	"image"
	"image/color"
	"log"
	"math"
	"os"
	"time"

	"gocv.io/x/gocv"
)

func fpsStart() time.Time {
	return time.Now()
}

func fpsUpdate(marker time.Time, count int) (float64, float64, time.Time) {
	tdelta := time.Since(marker).Seconds()
	fps := float64(count) / tdelta
	return fps, tdelta, time.Now()
}

func normalizeRmse(rmse float64) float64 {
	return math.Sqrt(math.Abs(rmse)) / 255.0
}

func processFrame(gray *gocv.Mat, diff1 *gocv.Mat, w, h int) (*gocv.Mat, []int, int, float64) {
	marker := color.RGBA{0, 0, 255, 0}
	palette := []color.RGBA{
		{31, 31, 229, 0}, {52, 161, 242, 0}, {211, 227, 247, 0},
		{68, 219, 187, 0}, {27, 206, 68, 0},
	}
	counts := make([]int, 0)
	total := w * h
	tStep := 5
	summ := 0.0

	for t := 0; t < 50; t += tStep {
		count := 0
		mi := t / 10
		marker = palette[mi]
		for y := 0; y < h; y++ {
			for x := 0; x < w; x++ {
				for ch := 0; ch < 3; ch++ {
					if diff1.GetVecbAt(y, x)[ch] > byte(t) {
						if t == 0 {
							summ += float64(diff1.GetVecbAt(y, x)[ch] * diff1.GetVecbAt(y, x)[ch])
						}
						gray.SetVecbAt(y, x, marker.RGBA())
						count++
					}
					break
				}
			}
		}
		counts = append(counts, count)
	}
	rmse := summ / float64(total)
	return gray, counts, total, rmse
}

func drawHeader(target *gocv.Mat, w, h int, counts []int, total int, rmse float64) *gocv.Mat {
	target.SetTo(color.RGBA{0, 0, 0, 0})
	text := ""
	if total > 0 {
		for _, c := range counts {
			t := c / 10
			prc := int(float64(c) / float64(total) * 100)
			text += fmt.Sprintf("[%d_%d%%]", t, prc)
		}
	}
	gocv.PutText(target, text, image.Pt(3, h-3), gocv.FontHersheyPlain, color.RGBA{255, 255, 255, 0}, 1, 8, false)
	gocv.PutText(target, fmt.Sprintf("RMSE:%f", normalizeRmse(rmse)), image.Pt(3, h/2-3), gocv.FontHersheyPlain, color.RGBA{255, 255, 255, 0}, 1, 8, false)
	return target
}

func processVideo(inPath, outPath string) bool {
	videoin, err := gocv.VideoCaptureFile(inPath)
	if err != nil {
		log.Fatalf("Error opening video file: %v", err)
	}
	defer videoin.Close()

	width := int(videoin.Get(gocv.VideoCaptureFrameWidth))
	height := int(videoin.Get(gocv.VideoCaptureFrameHeight))
	fps := videoin.Get(gocv.VideoCaptureFPS)

	if _, err := os.Stat(outPath); err == nil {
		os.Remove(outPath)
	}

	videoout, err := gocv.VideoWriterFile(outPath, "MP4V", fps, width, height+100, true)
	if err != nil {
		log.Fatalf("Error opening video writer: %v", err)
	}
	defer videoout.Close()

	last := gocv.NewMat()
	defer last.Close()

	out := gocv.NewMatWithSize(height+100, width, gocv.MatTypeCV8UC3)
	defer out.Close()

	for {
		frame := gocv.NewMat()
		defer frame.Close()
		if ok := videoin.Read(&frame); !ok {
			break
		}
		if frame.Empty() {
			continue
		}

		gray := gocv.NewMat()
		defer gray.Close()
		gocv.CvtColor(frame, &gray, gocv.ColorBGRToGray)
		gocv.CvtColor(gray, &gray, gocv.ColorGrayToBGR)

		total := width * height
		counts := make([]int, 0)
		rmse := 0.0

		if !last.Empty() {
			diff1 := gocv.NewMat()
			defer diff1.Close()
			gocv.AbsDiff(frame, last, &diff1)
			gray, counts, total, rmse = processFrame(&gray, &diff1, width, height)
		}

		outRegion := out.Region(image.Rect(0, 50, width, height+50))
		gray.CopyTo(&outRegion)
		out = drawHeader(&out, width, 50, counts, total, rmse)

		videoout.Write(out)
		last = frame.Clone()
	}
	return true
}

func main() {
	inPath := flag.String("inpath", "", "original file")
	outPath := flag.String("outpath", "", "target file")
	flag.Parse()

	if *inPath == "" {
		log.Fatal("no input file")
	}
	if *outPath == "" {
		*outPath = *inPath + ".fdiff.mp4"
	}

	if processVideo(*inPath, *outPath) {
		os.Exit(0)
	} else {
		os.Exit(-1)
	}
}
