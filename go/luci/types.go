package luci

import (
	"time"

	"github.com/apache/arrow/go/v13/arrow"
)

// Nugget represents a Luci Nugget token
type Nugget struct {
	NuggetID       string  `json:"nuggetId"`
	Creator        string  `json:"creator"`
	ResonanceUnits int     `json:"resonanceUnits"` // usually 10
	CapitalTime    int64   `json:"capitalTime"`
	ResonanceTime  float64 `json:"resonanceTime"`
	Authenticity   int     `json:"authenticityScore"` // 0-1000
	CreationUnix   int64   `json:"creationTimestamp"`
	AgentDID       string  `json:"agentDID"`
	IsActive       bool    `json:"isActive"`
}

// Coin represents a higher-order token minted by Chrysalis Fold
type Coin struct {
	CoinID      string  `json:"coinId"`
	Owner       string  `json:"owner"`
	FusionScore float64 `json:"fusionScore"`
	CreatedUnix int64   `json:"createdTimestamp"`
	Constituent []string
}

// ChrysalisRequest represents a request to fold nuggets into a coin
type ChrysalisRequest struct {
	Requester string   `json:"requester"`
	NuggetIDs []string `json:"nuggetIds"`
	Folder    string   `json:"folder"`
}

// DecisionRecord stores a decision outcome (Luciticy/Kobayashi) for audit
type DecisionRecord struct {
	DecisionID string    `json:"decisionId"`
	Actor      string    `json:"actor"`
	Action     string    `json:"action"`
	Scores     []float64 `json:"scores"`
	Weights    []float64 `json:"weights"`
	Result     string    `json:"result"`
	Timestamp  int64     `json:"timestamp"`
}

// HarmMetrics captures vectorized harm information for Kobayashi calculation
type HarmMetrics struct {
	Irreversibility float64 // 0..1
	ConsentPenalty  float64 // 0..1 (1=fully without consent)
	DignityLoss     float64 // 0..1
	FutureRestore   float64 // 0..1 (higher is better)
}

// Option is a candidate choice in a Kobayashi Maru scenario
type Option struct {
	ID    string
	Label string
	Harm  HarmMetrics
}

// Arrow schemas (used when serializing to Arrow IPC / tables)
func NuggetArrowSchema() *arrow.Schema {
	return arrow.NewSchema([]arrow.Field{
		{Name: "nuggetId", Type: arrow.BinaryTypes.String},
		{Name: "creator", Type: arrow.BinaryTypes.String},
		{Name: "resonanceUnits", Type: arrow.PrimitiveTypes.Int32},
		{Name: "capitalTime", Type: arrow.PrimitiveTypes.Int64},
		{Name: "resonanceTime", Type: arrow.PrimitiveTypes.Float64},
		{Name: "authenticityScore", Type: arrow.PrimitiveTypes.Int32},
		{Name: "creationTimestamp", Type: arrow.PrimitiveTypes.Int64},
		{Name: "agentDID", Type: arrow.BinaryTypes.String},
		{Name: "isActive", Type: arrow.FixedWidthTypes.Boolean},
	}, nil)
}

func CoinArrowSchema() *arrow.Schema {
	return arrow.NewSchema([]arrow.Field{
		{Name: "coinId", Type: arrow.BinaryTypes.String},
		{Name: "owner", Type: arrow.BinaryTypes.String},
		{Name: "fusionScore", Type: arrow.PrimitiveTypes.Float64},
		{Name: "createdTimestamp", Type: arrow.PrimitiveTypes.Int64},
		{Name: "constituent", Type: arrow.ListOf(arrow.BinaryTypes.String)},
	}, nil)
}

func DecisionArrowSchema() *arrow.Schema {
	return arrow.NewSchema([]arrow.Field{
		{Name: "decisionId", Type: arrow.BinaryTypes.String},
		{Name: "actor", Type: arrow.BinaryTypes.String},
		{Name: "action", Type: arrow.BinaryTypes.String},
		{Name: "scores", Type: arrow.ListOf(arrow.PrimitiveTypes.Float64)},
		{Name: "weights", Type: arrow.ListOf(arrow.PrimitiveTypes.Float64)},
		{Name: "result", Type: arrow.BinaryTypes.String},
		{Name: "timestamp", Type: arrow.PrimitiveTypes.Int64},
	}, nil)
}

// Utility: current unix timestamp
func NowUnix() int64 { return time.Now().Unix() }
