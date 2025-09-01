package main

import (
	"errors"
	"fmt"
	"image"
	"image/color"
	"math"
	"os"
	"path/filepath"
	"time"

	"gocv.io/x/gocv"
)

func fpsStart() time.Time {
	return time.Now()
}

func fpsUpdate(marker time.Time, count int) (float64, float64, time.Time) {
	tdelta := time.Since(marker)
	fps := float64(count) / tdelta.Seconds()
	return fps, tdelta.Seconds(), time.Now()
}

func normalizeRmse(rmse float64) float64 {
	return math.Sqrt(math.Abs(rmse)) / 255.0
}

func processFrame(gray *gocv.Mat, diff1 *gocv.Mat, w, h int) (*gocv.Mat, []struct{ T, Count int }, int, float64) {
	palette := [][]int{
		{31, 31, 229}, {52, 161, 242}, {211, 227, 247}, {68, 219, 187}, {27, 206, 68},
	}
	counts := []struct{ T, Count int }{}
	total := w * h
	tStep := 5
	summ := 0.0

	for t := 0; t < 50; t += tStep {
		count := 0
		mi := t / 10
		marker := palette[mi]
		for y := 0; y < h; y++ {
			for x := 0; x < w; x++ {
				ch := diff1.GetVecbAt(y, x)
				if ch[0] > uint8(t) || ch[1] > uint8(t) || ch[2] > uint8(t) {
					if t == 0 {
						summ += math.Pow(float64(ch[0]), 2) + math.Pow(float64(ch[1]), 2) + math.Pow(float64(ch[2]), 2)
					}
					gray.SetVecbAt(y, x, gocv.Vecb{B: uint8(marker[0]), G: uint8(marker[1]), R: uint8(marker[2])})
					count++
				}
			}
		}
		counts = append(counts, struct{ T, Count int }{t, count})
	}

	rmse := summ / float64(total)
	return gray, counts, total, rmse
}

func drawHeader(target *gocv.Mat, w, h int, counts []struct{ T, Count int }, total int, rmse float64) {
	gocv.Rectangle(target, image.Rect(0, 0, w, h), color.RGBA{0, 0, 0, 0}, -1)
	text := ""
	if total > 0 {
		for _, c := range counts {
			prc := int(float64(c.Count) / float64(total) * 100)
			text += fmt.Sprintf("[%d_%d%%]", c.T, prc)
		}
	}
	gocv.PutText(target, text, image.Pt(3, h-3), gocv.FontHersheyPlain, 1, color.RGBA{255, 255, 255, 255}, 1)
	gocv.PutText(target, fmt.Sprintf("RMSE:%f", normalizeRmse(rmse)), image.Pt(3, h/2-3), gocv.FontHersheyPlain, 1, color.RGBA{255, 255, 255, 255}, 1)
}

func drawFooter(target *gocv.Mat, y, w, h int, rmse float64) {
	gocv.Rectangle(target, image.Rect(0, y, w, y+h), color.RGBA{0, 0, 0, 0}, -1)
	margin := 3
	barH := 8
	barW := w - 2*margin
	start := image.Pt(margin, y+margin)
	end := image.Pt(barW+margin, y+margin+barH)
	inEnd := image.Pt(int(float64(barW)*normalizeRmse(rmse))+margin, y+margin+barH)

	gocv.Rectangle(target, image.Rect(start.X, start.Y, inEnd.X, inEnd.Y), color.RGBA{255, 255, 255, 255}, -1)
	gocv.Rectangle(target, image.Rect(start.X, start.Y, end.X, end.Y), color.RGBA{255, 255, 255, 255}, 1)
}

func processVideo(inPath, outPath string) bool {
	headerHeight := 64
	footerHeight := 24

	video, err := gocv.VideoCaptureFile(inPath)
	if err != nil {
		fmt.Printf("Error opening video: %v\n", err)
		return false
	}
	defer video.Close()

	total := int(video.Get(gocv.VideoCaptureFrameCount))
	w := int(video.Get(gocv.VideoCaptureFrameWidth))
	h := int(video.Get(gocv.VideoCaptureFrameHeight))
	fps := video.Get(gocv.VideoCaptureFPS)

	if _, err := os.Stat(outPath); err == nil {
		os.Remove(outPath)
	}

	outHeight := h + headerHeight + footerHeight
	writer, err := gocv.VideoWriterFile(outPath, "mp4v", fps, w, outHeight, true)
	if err != nil {
		fmt.Printf("Error creating writer: %v\n", err)
		return false
	}
	defer writer.Close()

	out := gocv.NewMatWithSize(outHeight, w, gocv.MatTypeCV8UC3)
	last := gocv.NewMat()
	defer last.Close()

	fmt.Printf("Processing %d frames...\n", total)
	for i := 0; i < total; i++ {
		frame := gocv.NewMat()
		if ok := video.Read(&frame); !ok {
			break
		}
		defer frame.Close()

		gray := gocv.NewMat()
		gocv.CvtColor(frame, &gray, gocv.ColorBGRToGray)
		gocv.CvtColor(gray, &gray, gocv.ColorGrayToBGR)

		var counts []struct{ T, Count int }
		totalPixels := w * h
		rmse := 0.0

		if !last.Empty() {
			diff := gocv.NewMat()
			gocv.AbsDiff(frame, last, &diff)
			defer diff.Close()

			gray, counts, totalPixels, rmse = processFrame(&gray, &diff, w, h)
		}

		region := out.Region(image.Rect(0, headerHeight, w, headerHeight+h))
		gray.CopyTo(&region)
		region.Close()

		drawHeader(&out, w, headerHeight, counts, totalPixels, rmse)
		drawFooter(&out, headerHeight+h, w, footerHeight, rmse)

		writer.Write(out)
		last = frame.Clone()
	}

	return true
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: frozen <input> [output]")
		os.Exit(1)
	}

	inPath := os.Args[1]
	outPath := "output.mp4"
	if len(os.Args) >= 3 {
		outPath = os.Args[2]
	} else {
		outPath = filepath.Base(inPath) + ".fdiff.mp4"
	}

	if _, err := os.Stat(inPath); errors.Is(err, os.ErrNotExist) {
		fmt.Printf("File not found: %s\n", inPath)
		os.Exit(1)
	}

	if ok := processVideo(inPath, outPath); !ok {
		os.Exit(1)
	}
}
